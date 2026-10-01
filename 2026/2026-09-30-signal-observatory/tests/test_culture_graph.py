"""Tests for Culture Migration Graph analyzer."""

from datetime import UTC, datetime, timedelta

from observatory.culture_graph import CultureMigrationAnalyzer
from observatory.models import Artifact, ContentType, Platform, TimestampQuality


class TestCultureMigrationGraph:
    """Test cross-platform culture migration tracing, mutation, and graphing."""

    def test_single_platform_trace(self) -> None:
        t0 = datetime(2026, 9, 10, 12, 0, tzinfo=UTC)
        artifacts = [
            Artifact(
                platform=Platform.REDDIT,
                native_id="red_1",
                content_type=ContentType.POST,
                text="Just tried the powdered cheese tacos at In-A-Tub.",
                author_handle="user_a",
                published_at=t0,
                published_at_quality=TimestampQuality.SOURCE_EXACT,
            ),
            Artifact(
                platform=Platform.REDDIT,
                native_id="red_2",
                content_type=ContentType.POST,
                text="In-A-Tub fried tacos are an absolute Northland institution.",
                author_handle="user_b",
                published_at=t0 + timedelta(hours=4),
                published_at_quality=TimestampQuality.SOURCE_EXACT,
            ),
        ]

        analyzer = CultureMigrationAnalyzer()
        graph = analyzer.trace("tacos", artifacts=artifacts)

        assert graph.total_artifacts_analyzed == 2
        assert len(graph.platforms_observed) == 1
        assert graph.platforms_observed[0] == Platform.REDDIT
        assert graph.time_to_second_platform_hours is None
        assert graph.creators_before_crossover == 2
        assert len(graph.hops) == 0

    def test_multi_platform_migration_and_mutation(self) -> None:
        t0 = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)
        # Stage 1: TikTok grassroots clip
        art1 = Artifact(
            platform=Platform.TIKTOK,
            native_id="tt_01",
            content_type=ContentType.VIDEO,
            text="pov: underground secret rave at 12th street warehouse #kcrave #techno",
            author_handle="rave_kid",
            published_at=t0,
            published_at_quality=TimestampQuality.SOURCE_EXACT,
        )
        # Stage 1 duplicate creator on TikTok
        art2 = Artifact(
            platform=Platform.TIKTOK,
            native_id="tt_02",
            content_type=ContentType.VIDEO,
            text="insane sound system at the west bottom warehouse rave",
            author_handle="bass_head",
            published_at=t0 + timedelta(hours=6),
            published_at_quality=TimestampQuality.SOURCE_EXACT,
        )
        # Stage 2: Reddit discussion (hop 1)
        art3 = Artifact(
            platform=Platform.REDDIT,
            native_id="rd_01",
            content_type=ContentType.POST,
            text="Anyone know who is organizing the underground warehouse raves in West Bottoms?",
            author_handle="curious_local",
            published_at=t0 + timedelta(hours=18),
            published_at_quality=TimestampQuality.SOURCE_EXACT,
        )
        # Stage 3: Web news coverage (hop 2, mainstream)
        art4 = Artifact(
            platform=Platform.WEB,
            native_id="web_01",
            content_type=ContentType.ARTICLE,
            text=(
                "Kansas City officials address unpermitted warehouse party "
                "complaints in West Bottoms"
            ),
            author_handle="kc_star_reporter",
            published_at=t0 + timedelta(hours=60),
            published_at_quality=TimestampQuality.SOURCE_DATE_ONLY,
        )

        analyzer = CultureMigrationAnalyzer()
        graph = analyzer.trace("rave", artifacts=[art1, art2, art3, art4])

        assert graph.total_artifacts_analyzed == 4
        assert graph.platforms_observed == [Platform.TIKTOK, Platform.REDDIT, Platform.WEB]
        assert graph.earliest_appearance is not None
        assert graph.earliest_appearance.platform == Platform.TIKTOK
        assert graph.earliest_appearance.author == "rave_kid"

        # Check latency
        assert graph.time_to_second_platform_hours == 18.0
        assert graph.time_to_mainstream_hours == 60.0

        # Creators before crossover (rave_kid, bass_head)
        assert graph.creators_before_crossover == 2

        # Check hops
        assert len(graph.hops) == 2

        hop1 = graph.hops[0]
        assert hop1.source_node.platform == Platform.TIKTOK
        assert hop1.target_node.platform == Platform.REDDIT
        assert hop1.latency_hours == 18.0
        assert hop1.jaccard_divergence > 0.0

        hop2 = graph.hops[1]
        assert hop2.source_node.platform == Platform.REDDIT
        assert hop2.target_node.platform == Platform.WEB
        assert hop2.latency_hours == 42.0  # 60h - 18h

        # Verify Mermaid diagram and Markdown report
        assert "flowchart TD" in graph.mermaid_diagram
        assert "sg_tiktok" in graph.mermaid_diagram
        assert "sg_reddit" in graph.mermaid_diagram
        assert "sg_web" in graph.mermaid_diagram

        md = graph.summary_markdown()
        assert "# Culture Migration Graph: 'rave'" in md
        assert "Hop 1: tiktok -> reddit" in md
        assert "Time to Mainstream/Press" in md
        assert "60.0 hours" in md
