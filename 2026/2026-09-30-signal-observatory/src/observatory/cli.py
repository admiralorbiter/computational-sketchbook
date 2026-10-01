"""Observatory CLI — the instrument panel for the AI research harness.

This CLI provides the deterministic tools that the Antigravity harness
operates. Every command does exactly one thing, returns structured data,
and records provenance.

All collectors use direct scraping — no API keys required:
- Bluesky: AT Protocol public AppView (unauthenticated HTTP)
- YouTube: yt-dlp for search/metadata, youtube-transcript-api for transcripts
- Reddit: old.reddit.com web scraping with BeautifulSoup

Usage:
    observatory search bluesky --query "topic" --limit 50
    observatory search youtube --query "topic" --limit 20
    observatory search reddit --query "topic" --subreddit kansascity
    observatory fetch bluesky <at-uri>
    observatory fetch youtube <video-id>
    observatory fetch reddit <url>
    observatory transcript <video-id>
    observatory corpus-stats
    observatory sql "SELECT * FROM artifacts LIMIT 10"
"""

import asyncio
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

# Ensure UTF-8 output on Windows shells to prevent cp1252 charmap encoding errors
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from observatory.collectors.base import BaseCollector
from observatory.collectors.bluesky import BlueskyCollector
from observatory.collectors.footage import CitizenFootageCollector
from observatory.collectors.reddit import RedditCollector
from observatory.collectors.reviews import ReviewsCollector
from observatory.collectors.snapchat import SnapchatCollector
from observatory.collectors.web import WebCollector
from observatory.collectors.youtube import YouTubeCollector
from observatory.config import get_settings
from observatory.events import EventLedger, EventMilestone
from observatory.media import download_media_footage
from observatory.store.corpus import CorpusStore

app = typer.Typer(
    name="observatory",
    help="Signal Observatory — public discourse research tools. No API keys required.",
    no_args_is_help=True,
)
console = Console()

SUPPORTED_PLATFORMS = {
    "bluesky",
    "youtube",
    "reddit",
    "web",
    "reviews",
    "citizen",
    "footage",
    "snapchat",
}


def _get_collector(platform: str) -> BaseCollector:
    """Get the appropriate collector for a platform.

    Args:
        platform: Platform name (bluesky, youtube, reddit, web,
            reviews, citizen, footage, snapchat).

    Returns:
        Instantiated collector.

    Raises:
        typer.Exit: If platform is not supported.
    """
    match platform:
        case "bluesky":
            return BlueskyCollector()
        case "youtube":
            return YouTubeCollector()
        case "reddit":
            return RedditCollector()
        case "web":
            return WebCollector()
        case "reviews":
            return ReviewsCollector()
        case "citizen" | "footage":
            return CitizenFootageCollector()
        case "snapchat":
            return SnapchatCollector()
        case _:
            rprint(f"[red]Unknown platform: '{platform}'[/red]")
            rprint(f"[dim]Available: {', '.join(sorted(SUPPORTED_PLATFORMS))}[/dim]")
            raise typer.Exit(1)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@app.command()
def search(
    platform: str = typer.Argument(help="Platform to search (bluesky, youtube, reddit)."),
    query: str = typer.Option(..., "--query", "-q", help="Search query string."),
    limit: int = typer.Option(50, "--limit", "-n", help="Max results to return."),
    since: str | None = typer.Option(None, "--since", help="Lower time bound (ISO-8601)."),
    until: str | None = typer.Option(None, "--until", help="Upper time bound (ISO-8601)."),
    sort: str = typer.Option("latest", "--sort", help="Sort order (latest, top, relevance)."),
    subreddit: str | None = typer.Option(
        None, "--subreddit", "-r", help="Reddit: subreddit to search within."
    ),
    time_filter: str = typer.Option(
        "all",
        "--time-filter",
        "-t",
        help="Reddit: time filter (hour, day, week, month, year, all).",
    ),
    run_id: str = typer.Option("", "--run-id", help="Run ID for provenance tracking."),
    store: bool = typer.Option(True, "--store/--no-store", help="Store results in corpus."),
) -> None:
    """Search a platform for posts matching a query."""
    collector = _get_collector(platform)
    query_id = str(uuid.uuid4())[:8]
    effective_run_id = run_id or f"adhoc_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"

    async def _search() -> None:
        try:
            # Build platform-specific kwargs
            kwargs = {}
            if platform == "reddit":
                if subreddit:
                    kwargs["subreddit"] = subreddit
                kwargs["time_filter"] = time_filter
                kwargs["sort"] = sort
            elif platform == "bluesky":
                kwargs["sort"] = sort

            artifacts, next_cursor, raw_records = await collector.search(
                query,
                limit=limit,
                since=since,
                until=until,
                **kwargs,
            )

            # Set provenance on artifacts
            for a in artifacts:
                a.query_id = query_id
                a.run_id = effective_run_id

            if store:
                corpus = CorpusStore()
                corpus.store_raw(raw_records, platform=platform, query_id=query_id)
                new_count = corpus.store_artifacts(artifacts)
                dup_count = len(artifacts) - new_count
                rprint(
                    f"[green]Stored {new_count} new artifacts[/green] "
                    f"({len(artifacts)} total, {dup_count} duplicates)"
                )

            # Display results
            table = Table(title=f"Search Results: {query} ({platform})", show_lines=True)
            table.add_column("#", style="dim", width=4)
            table.add_column("Author", style="cyan", width=25)
            table.add_column("Text", width=60)
            table.add_column("Score", justify="right", width=8)
            table.add_column("Published", width=20)

            for i, artifact in enumerate(artifacts, 1):
                text = (artifact.text or "")[:100]
                if len(artifact.text or "") > 100:
                    text += "..."
                published = str(artifact.published_at)[:19] if artifact.published_at else "?"
                score = str(artifact.engagement.likes) if artifact.engagement else "0"
                table.add_row(str(i), artifact.author_handle or "?", text, score, published)

            console.print(table)

            # Output metadata
            rprint(f"\n[dim]Query ID: {query_id}[/dim]")
            rprint(f"[dim]Run ID: {effective_run_id}[/dim]")
            if next_cursor:
                rprint(f"[dim]Next cursor: {next_cursor}[/dim]")
            rprint(f"[dim]Total results: {len(artifacts)}[/dim]")

        finally:
            if hasattr(collector, "close"):
                await collector.close()

    asyncio.run(_search())


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------


@app.command()
def fetch(
    platform: str = typer.Argument(help="Platform (bluesky, youtube, reddit)."),
    native_id: str = typer.Argument(help="Platform-native ID (AT URI, video ID, URL)."),
    store: bool = typer.Option(True, "--store/--no-store", help="Store result in corpus."),
) -> None:
    """Fetch a single item by its native platform ID."""
    collector = _get_collector(platform)

    async def _fetch() -> None:
        try:
            artifact, raw = await collector.fetch(native_id)

            if not artifact:
                rprint(f"[yellow]Not found: {native_id}[/yellow]")
                raise typer.Exit(1)

            if store and raw:
                corpus = CorpusStore()
                corpus.store_raw([raw], platform=platform, query_id="fetch")
                new_count = corpus.store_artifacts([artifact])
                rprint(f"[green]Stored {new_count} artifact(s)[/green]")

            rprint(f"\n[bold]Artifact ID:[/bold] {artifact.artifact_id}")
            rprint(f"[bold]Platform:[/bold] {artifact.platform.value}")
            rprint(f"[bold]Author:[/bold] {artifact.author_handle}")
            rprint(f"[bold]Published:[/bold] {artifact.published_at}")
            rprint(f"[bold]URL:[/bold] {artifact.canonical_url}")
            rprint(f"[bold]Text:[/bold]\n{artifact.text}")
            if artifact.engagement:
                rprint(
                    f"[bold]Engagement:[/bold] "
                    f"{artifact.engagement.likes} score/likes, "
                    f"{artifact.engagement.reposts} reposts, "
                    f"{artifact.engagement.replies} replies"
                )
                if artifact.engagement.views is not None:
                    rprint(f"[bold]Views:[/bold] {artifact.engagement.views:,}")

        finally:
            if hasattr(collector, "close"):
                await collector.close()

    asyncio.run(_fetch())


# ---------------------------------------------------------------------------
# Transcript (YouTube-specific)
# ---------------------------------------------------------------------------


@app.command()
def transcript(
    video_id: str = typer.Argument(help="YouTube video ID."),
    store: bool = typer.Option(True, "--store/--no-store", help="Store as annotation in corpus."),
) -> None:
    """Fetch the transcript for a YouTube video (no API key needed)."""
    collector = YouTubeCollector()

    async def _transcript() -> None:
        text = await collector.fetch_transcript(video_id)
        if not text:
            rprint(f"[yellow]No transcript available for {video_id}[/yellow]")
            raise typer.Exit(1)

        if store:
            from observatory.models import Annotation, AnnotationType, artifact_id

            ann = Annotation(
                annotation_id=str(uuid.uuid4())[:12],
                artifact_id=artifact_id("youtube", video_id),
                annotation_type=AnnotationType.TRANSCRIPTION,
                value=text,
                model="youtube-captions",
                model_version="auto",
            )
            corpus = CorpusStore()
            corpus.store_annotations([ann])
            rprint("[green]Stored transcript as annotation[/green]")

        # Show preview
        preview = text[:500]
        if len(text) > 500:
            preview += "..."
        rprint(f"\n[bold]Transcript ({len(text)} chars):[/bold]\n{preview}")

    asyncio.run(_transcript())


# ---------------------------------------------------------------------------
# Comments Harvesting (Social Listening)
# ---------------------------------------------------------------------------


@app.command()
def comments(
    video_id: str = typer.Argument(help="YouTube video ID (e.g. MT15d2E7H9g)."),
    limit: int = typer.Option(50, "--limit", "-n", help="Max comments to harvest."),
    store: bool = typer.Option(True, "--store/--no-store", help="Store comments in corpus."),
) -> None:
    """Harvest real user comments from a YouTube video discussion thread.

    Pulls local reactions, arguments, and commentary without requiring any API keys.
    """
    collector = YouTubeCollector()

    async def _comments() -> None:
        artifacts, raw = await collector.fetch_comments(video_id, max_comments=limit)
        if not artifacts:
            rprint(f"[yellow]No comments found or discussion disabled for {video_id}[/yellow]")
            return

        if store:
            corpus = CorpusStore()
            query_id = f"comments_{video_id[:8]}"
            corpus.store_raw(raw, platform="youtube", query_id=query_id)
            new_count = corpus.store_artifacts(artifacts)
            rprint(
                f"[green]Stored {new_count} comments in corpus[/green] ({len(artifacts)} fetched)"
            )

        table = Table(title=f"User Comments ({video_id})", show_lines=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Author", style="cyan", width=22)
        table.add_column("Comment", width=70)
        table.add_column("Likes", justify="right", width=6)

        for i, a in enumerate(artifacts[:25], 1):
            text = (a.text or "").replace("\n", " ")[:120]
            if len(a.text or "") > 120:
                text += "..."
            likes = str(a.engagement.likes) if a.engagement else "0"
            table.add_row(str(i), a.author_handle or "?", text, likes)

        console.print(table)
        if len(artifacts) > 25:
            rprint(f"[dim]...and {len(artifacts) - 25} more comments stored in Parquet.[/dim]")

    asyncio.run(_comments())


# ---------------------------------------------------------------------------
# Corpus Stats
# ---------------------------------------------------------------------------


@app.command(name="corpus-stats")
def corpus_stats() -> None:
    """Display summary statistics about the evidence corpus."""
    corpus = CorpusStore()
    stats = corpus.corpus_stats()

    table = Table(title="Corpus Statistics")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Total Artifacts", str(stats["artifacts"]))
    table.add_row("Total Annotations", str(stats["annotations"]))
    table.add_row("Platforms", ", ".join(stats["platforms"]) if stats["platforms"] else "none")

    if stats["date_range"]:
        table.add_row("Earliest", stats["date_range"]["earliest"][:19])
        table.add_row("Latest", stats["date_range"]["latest"][:19])

    console.print(table)


# ---------------------------------------------------------------------------
# SQL Query
# ---------------------------------------------------------------------------


@app.command(name="sql")
def sql_query(
    query: str = typer.Argument(help="SQL query to execute against the corpus."),
) -> None:
    """Execute a DuckDB SQL query against the corpus.

    Available views: 'artifacts', 'annotations'.
    You can also query Parquet files directly with glob patterns.
    """
    corpus = CorpusStore()
    try:
        result = corpus.query(query)
        if result.height == 0:
            rprint("[dim]Query returned 0 rows.[/dim]")
            return

        table = Table(title="Query Result", show_lines=True)
        for col_name in result.columns:
            table.add_column(str(col_name), overflow="fold")

        for row in result.iter_rows():
            table.add_row(*[str(val) if val is not None else "[dim]null[/dim]" for val in row])

        console.print(table)
        rprint(f"[dim]{result.height} row(s) returned[/dim]")
    except Exception as e:
        rprint(f"[red]Query error:[/red] {e}")
        raise typer.Exit(1) from e


# ---------------------------------------------------------------------------
# Inquiry Execution
# ---------------------------------------------------------------------------


@app.command()
def inquire(
    inquiry_path: str = typer.Argument(
        ...,
        help="Path to the inquiry YAML file (e.g. inquiries/2026-09-kc-streetcar-transit.yaml).",
    ),
    auto_transcribe: bool = typer.Option(
        True,
        "--transcribe/--no-transcribe",
        help="Automatically extract transcripts for video artifacts.",
    ),
) -> None:
    """Execute a structured research inquiry end-to-end.

    Creates an auditable run directory in runs/<run-id>/ with queries,
    immutable raw responses, normalized Parquet artifacts, and a summary memo.
    """
    from pathlib import Path

    from observatory.inquiry_runner import InquiryRunner, load_inquiry

    path = Path(inquiry_path)
    if not path.exists():
        rprint(f"[red]Inquiry file not found: {inquiry_path}[/red]")
        raise typer.Exit(1)

    try:
        inquiry_obj = load_inquiry(path)
    except Exception as e:
        rprint(f"[red]Error parsing inquiry YAML:[/red] {e}")
        raise typer.Exit(1) from e

    rprint(f"[bold cyan]Launching Inquiry Run:[/bold cyan] {inquiry_obj.id}")
    rprint(f"[dim]Question: {inquiry_obj.question.strip()}[/dim]")
    rprint(f"[dim]Platforms: {', '.join(p.value for p in inquiry_obj.platforms)}[/dim]\n")

    runner = InquiryRunner(inquiry_obj)

    async def _run() -> None:
        manifest = await runner.execute(auto_transcribe=auto_transcribe)
        rprint(f"\n[bold green]Inquiry Run Completed:[/bold green] {manifest.run_id}")
        rprint(f"[dim]Run Directory: {runner.run_dir}[/dim]")
        rprint(f"- Total queries executed: {manifest.total_queries}")
        rprint(f"- Total artifacts collected: {manifest.total_artifacts}")
        rprint(f"- Media transcripts enriched: {manifest.total_media}")
        rprint(f"\n[green]Run summary memo written to:[/green] {runner.run_dir / 'RUN_SUMMARY.md'}")
        report_file = runner.run_dir / "ANALYSIS_REPORT.md"
        if report_file.exists():
            rprint(f"[green]Discourse analysis report generated at:[/green] {report_file}")

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# Discourse Synthesis & Drama Analysis
# ---------------------------------------------------------------------------


@app.command()
def analyze(
    run_id: str = typer.Argument(
        ...,
        help="Run ID to analyze (e.g. run_<inquiry_id>_<timestamp> or 'latest').",
    ),
) -> None:
    """Perform discourse synthesis, viewpoint faction mapping, and drama detection.

    Generates ANALYSIS_REPORT.md and stores Level 3 annotations in Parquet.
    """
    from observatory.analysis import DiscourseAnalyzer
    from observatory.config import get_settings

    settings = get_settings()
    target_run_id = run_id

    if run_id == "latest":
        runs = sorted(
            settings.runs_dir.glob("run_*"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        if not runs:
            rprint("[red]No runs found in runs/ directory.[/red]")
            raise typer.Exit(1)
        target_run_id = runs[0].name

    rprint(f"[bold cyan]Analyzing Run:[/bold cyan] {target_run_id}")
    analyzer = DiscourseAnalyzer(settings=settings)

    try:
        res = analyzer.analyze_run(target_run_id)
        if res.get("status") == "empty":
            rprint(f"[yellow]{res['message']}[/yellow]")
            return

        rprint(f"\n[green]Analyzed {res['total_artifacts']} artifacts[/green]")
        rprint(
            f"[bold yellow]Flagged {res['total_friction_events']} "
            "friction / drama incidents[/bold yellow]"
        )
        rprint(f"[green]Stored {len(res['annotations'])} Level 3 annotations in Parquet[/green]\n")

        # Display Top Friction Incidents in Table
        if res["friction_events"]:
            table = Table(title="Top Friction & Drama Hotspots", show_lines=True)
            table.add_column("#", width=3)
            table.add_column("Author", style="cyan", width=18)
            table.add_column("Category", style="magenta", width=25)
            table.add_column("Direct Evidence Quote", width=65)
            table.add_column("Intensity", justify="right", width=9)

            for i, ev in enumerate(res["friction_events"][:8], 1):
                table.add_row(
                    str(i),
                    ev["author"][:18],
                    ", ".join(ev["categories"])[:25],
                    ev["excerpt"][:120] + ("..." if len(ev["excerpt"]) > 120 else ""),
                    str(ev["intensity"]),
                )
            console.print(table)

        report_path = settings.runs_dir / target_run_id / "ANALYSIS_REPORT.md"
        rprint(
            f"\n[bold green]Comprehensive Analysis Report generated at:[/bold green] {report_path}"
        )

    except Exception as e:
        rprint(f"[red]Analysis failed:[/red] {e}")
        raise typer.Exit(1) from e


@app.command()
def download_video(
    url_or_id: str = typer.Argument(help="Video URL (YouTube, TikTok, Facebook) or native ID."),
    output_dir: str | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory. Defaults to configured media_dir.",
    ),
    max_height: int = typer.Option(720, "--max-height", help="Maximum video resolution height."),
) -> None:
    """Download raw video footage and audio to disk with clean descriptive naming."""
    settings = get_settings()
    dest_dir = Path(output_dir) if output_dir else settings.media_dir
    console.print(f"[bold cyan]Downloading footage:[/bold cyan] {url_or_id} -> {dest_dir}")
    path, meta = download_media_footage(url_or_id, output_dir=dest_dir, max_height=max_height)
    if path and path.exists():
        size_mb = path.stat().st_size / (1024 * 1024)
        console.print(f"[bold green]✓ Downloaded raw footage:[/bold green] {path.name}")
        console.print(f"[dim]Saved to: {path} ({size_mb:.1f} MB)[/dim]")
    else:
        console.print("[bold red]✗ Failed to download video footage.[/bold red]")


# ---------------------------------------------------------------------------
# Living Event Ledger Subcommands
# ---------------------------------------------------------------------------

event_app = typer.Typer(
    name="event",
    help="Living Event Ledger — track events, attach media clips and timeline milestones.",
)
app.add_typer(event_app, name="event")


@event_app.command("list")
def event_list() -> None:
    """List all tracked events in the living ledger."""
    ledger = EventLedger()
    events = ledger.list_events()
    if not events:
        console.print("[dim]No events currently tracked in the ledger.[/dim]")
        return

    table = Table(title="Tracked Historical & Developing Events", show_lines=True)
    table.add_column("Event ID", style="cyan", width=28)
    table.add_column("Title", style="bold white", width=30)
    table.add_column("Category", style="magenta", width=14)
    table.add_column("Location", style="yellow", width=22)
    table.add_column("Milestones", justify="right", width=10)
    table.add_column("Media Files", justify="right", width=11)
    table.add_column("Status", width=10)

    for ev in events:
        table.add_row(
            ev.id,
            ev.title,
            ev.category,
            ev.location,
            str(len(ev.milestones)),
            str(len(ev.media_files)),
            ev.status.upper(),
        )
    console.print(table)


@event_app.command("create")
def event_create(
    event_id: str = typer.Argument(help="Unique slug for the event (e.g. 2026-09-dodge-city-ice)"),
    title: str = typer.Option(..., "--title", "-t", help="Descriptive event title"),
    category: str = typer.Option("general", "--category", "-c", help="Event category"),
    location: str = typer.Option("", "--location", "-l", help="Geographic location"),
    summary: str = typer.Option("", "--summary", "-s", help="Background summary"),
    date_start: str = typer.Option("", "--date", "-d", help="Start date (YYYY-MM-DD)"),
) -> None:
    """Create a new tracked event in the ledger."""
    ledger = EventLedger()
    ev = ledger.create_event(
        event_id=event_id,
        title=title,
        category=category,
        location=location,
        summary=summary,
        date_start=date_start,
    )
    console.print(f"[bold green]✓ Created tracked event:[/bold green] {ev.id} ({ev.title})")


@event_app.command("add-milestone")
def event_add_milestone(
    event_id: str = typer.Argument(help="ID of the event"),
    timestamp: str = typer.Option(..., "--time", "-t", help="Timestamp (YYYY-MM-DD or ISO)"),
    headline: str = typer.Option(..., "--headline", "-h", help="Milestone headline"),
    description: str = typer.Option("", "--desc", "-d", help="Detailed description / excerpt"),
    author: str | None = typer.Option(None, "--author", "-a", help="Eyewitness / author handle"),
    platform: str | None = typer.Option(None, "--platform", "-p", help="Source platform"),
    source_url: str | None = typer.Option(None, "--url", "-u", help="Canonical source URL"),
    media_path: str | None = typer.Option(None, "--media", "-m", help="Path to local media clip"),
) -> None:
    """Add a chronological milestone observation to an event."""
    ledger = EventLedger()
    ev = ledger.get_event(event_id)
    if not ev:
        console.print(f"[bold red]✗ Event not found:[/bold red] {event_id}")
        raise typer.Exit(1)

    m = EventMilestone(
        timestamp=timestamp,
        headline=headline,
        description=description,
        author=author,
        platform=platform,
        source_url=source_url,
        media_path=media_path,
    )
    ev.add_milestone(m)
    ledger.save_event(ev)
    console.print(f"[bold green]✓ Added milestone to {event_id}:[/bold green] {m.headline}")


@event_app.command("timeline")
def event_timeline(
    event_id: str = typer.Argument(help="ID of the event to render"),
) -> None:
    """Display the full chronological timeline of an event."""
    ledger = EventLedger()
    md = ledger.generate_timeline_markdown(event_id)
    console.print(md)


if __name__ == "__main__":
    app()

