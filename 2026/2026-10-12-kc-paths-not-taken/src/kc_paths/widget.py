"""Interactive HTML5/JS/CSS game interface renderer for Jupyter Notebooks."""

import json
from pathlib import Path
from typing import Optional
from IPython.display import HTML
from .data_loader import load_locations, load_programs, load_sources, load_scenario


def render_playable_game(
    height: int = 780,
    width: str = "100%",
    initial_transport: str = "reliable"
) -> HTML:
    """Generate a self-contained, fully interactive playable game widget for Jupyter.

    Runs pure client-side HTML, CSS, Leaflet GIS mapping, and the exact state machine
    defined in the Vertical Slice 01 specification.
    """
    locations_data = load_locations()
    programs_data = load_programs()
    sources_data = load_sources()
    scenario_data = load_scenario()

    locations_json = json.dumps(locations_data)
    programs_json = json.dumps(programs_data)
    sources_json = json.dumps(sources_data)
    scenario_json = json.dumps(scenario_data)

    html_code = f"""
<div id="kc-game-container" style="width: {width}; height: {height}px; border: 1px solid #1e293b; border-radius: 12px; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; position: relative; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <style>
    #kc-game-container * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    .kc-header {{
      background: #1e293b;
      padding: 12px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #334155;
    }}
    .kc-title-group h2 {{
      font-size: 1.15rem;
      font-weight: 700;
      color: #38bdf8;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .kc-title-group p {{
      font-size: 0.8rem;
      color: #94a3b8;
    }}
    .kc-status-bar {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}
    .kc-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      background: #334155;
      color: #cbd5e1;
    }}
    .kc-badge.ap {{
      background: #0284c7;
      color: #ffffff;
    }}
    .kc-badge.transport {{
      background: #334155;
      color: #f1f5f9;
      border: 1px solid #475569;
    }}
    .kc-main {{
      display: grid;
      grid-template-columns: 1.1fr 1fr;
      height: calc(100% - 60px);
      position: relative;
    }}
    #kc-map {{
      width: 100%;
      height: 100%;
      background: #090d16;
    }}
    .kc-sidebar {{
      background: #0f172a;
      display: flex;
      flex-direction: column;
      height: 100%;
      border-left: 1px solid #1e293b;
      overflow-y: auto;
    }}
    .kc-panel-section {{
      padding: 16px;
      border-bottom: 1px solid #1e293b;
    }}
    .kc-section-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}
    .kc-section-header h3 {{
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #94a3b8;
      font-weight: 700;
    }}
    .kc-action-card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 12px;
      margin-bottom: 10px;
      transition: all 0.2s ease;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .kc-action-card:hover {{
      border-color: #38bdf8;
      background: #24344d;
    }}
    .kc-action-card.completed {{
      opacity: 0.6;
      border-color: #10b981;
      background: #064e3b22;
    }}
    .kc-action-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 8px;
    }}
    .kc-action-title {{
      font-size: 0.9rem;
      font-weight: 600;
      color: #f8fafc;
    }}
    .kc-action-cost {{
      font-size: 0.75rem;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      background: #0284c7;
      color: #ffffff;
      white-space: nowrap;
    }}
    .kc-action-desc {{
      font-size: 0.78rem;
      color: #94a3b8;
      line-height: 1.35;
    }}
    .kc-action-meta {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 4px;
    }}
    .kc-loc-tag {{
      font-size: 0.7rem;
      color: #cbd5e1;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}
    .kc-btn {{
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 600;
      cursor: pointer;
      border: none;
      transition: all 0.15s ease;
    }}
    .kc-btn-primary {{
      background: #0284c7;
      color: #ffffff;
    }}
    .kc-btn-primary:hover:not(:disabled) {{
      background: #0369a1;
    }}
    .kc-btn-primary:disabled {{
      background: #334155;
      color: #64748b;
      cursor: not-allowed;
    }}
    .kc-btn-outline {{
      background: transparent;
      border: 1px solid #475569;
      color: #94a3b8;
    }}
    .kc-btn-outline:hover {{
      border-color: #38bdf8;
      color: #38bdf8;
    }}
    .kc-history-list {{
      display: flex;
      flex-direction: column;
      gap: 8px;
      font-size: 0.78rem;
    }}
    .kc-history-item {{
      background: #182234;
      padding: 8px 10px;
      border-radius: 6px;
      border-left: 3px solid #38bdf8;
      color: #cbd5e1;
    }}
    .kc-drawer {{
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      width: 420px;
      background: #0f172a;
      border-left: 1px solid #334155;
      z-index: 1000;
      box-shadow: -10px 0 25px rgba(0,0,0,0.7);
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      transform: translateX(100%);
      transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      overflow-y: auto;
    }}
    .kc-drawer.open {{
      transform: translateX(0);
    }}
    .kc-modal-overlay {{
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(4px);
      z-index: 2000;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 24px;
    }}
    .kc-modal {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 24px;
      max-width: 580px;
      width: 100%;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .kc-source-tag {{
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      background: #064e3b;
      color: #34d399;
    }}
    .leaflet-popup-content-wrapper {{
      background: #1e293b;
      color: #f8fafc;
      border: 1px solid #334155;
      border-radius: 8px;
    }}
    .leaflet-popup-tip {{
      background: #1e293b;
    }}
  </style>

  <div class="kc-header">
    <div class="kc-title-group">
      <h2><span>📍</span> Kansas City — Paths Not Taken</h2>
      <p id="kc-scenario-sub">Mission 01: A Future in Healthcare · Ruskin High School</p>
    </div>
    <div class="kc-status-bar">
      <div class="kc-badge" id="kc-round-badge">Round 1 of 3</div>
      <div class="kc-badge ap" id="kc-ap-badge">2 AP Available</div>
      <div class="kc-badge transport" id="kc-transport-badge">🚗 Transport: Reliable</div>
      <button class="kc-btn kc-btn-outline" id="kc-why-btn" onclick="openEvidenceDrawer('general')">📚 Sources</button>
    </div>
  </div>

  <div class="kc-main">
    <div id="kc-map"></div>

    <div class="kc-sidebar">
      <div class="kc-panel-section">
        <div class="kc-section-header">
          <h3>Current Location Focus</h3>
          <span class="kc-badge" id="kc-focus-badge">Ruskin High School</span>
        </div>
        <p id="kc-focus-desc" style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.4;">
          Your home campus in Hickman Mills. Start by speaking with your counselor or researching district off-campus options.
        </p>
      </div>

      <div class="kc-panel-section" style="flex: 1;">
        <div class="kc-section-header">
          <h3>Available Planning Actions</h3>
          <span style="font-size: 0.75rem; color: #94a3b8;" id="kc-round-timer">Spend 2 AP to end round</span>
        </div>
        <div id="kc-actions-list">
          <!-- Dynamic Action Cards -->
        </div>
        <div style="margin-top: 12px; display: flex; justify-content: flex-end;">
          <button class="kc-btn kc-btn-outline" id="kc-advance-btn" onclick="handleAdvanceRound()">
            End Round 1 →
          </button>
        </div>
      </div>

      <div class="kc-panel-section" style="max-height: 220px; overflow-y: auto;">
        <div class="kc-section-header">
          <h3>Journey Timeline & Journal</h3>
        </div>
        <div class="kc-history-list" id="kc-history-list">
          <div style="color: #64748b; font-style: italic; font-size: 0.75rem;">No actions completed yet.</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Evidence Drawer -->
  <div class="kc-drawer" id="kc-evidence-drawer">
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 12px;">
      <h3 style="font-size: 1rem; color: #38bdf8; font-weight: 700;">Evidence & Provenance</h3>
      <button class="kc-btn kc-btn-outline" onclick="closeEvidenceDrawer()">✕ Close</button>
    </div>
    <div id="kc-drawer-content" style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5; display: flex; flex-direction: column; gap: 12px;">
      <!-- Populated dynamically -->
    </div>
  </div>

  <!-- Setup & Outcome Modals -->
  <div class="kc-modal-overlay" id="kc-modal-overlay">
    <div class="kc-modal" id="kc-modal-box">
      <!-- Dynamic modal content -->
    </div>
  </div>

  <script>
    (function() {{
      const locationsData = {locations_json};
      const programsData = {programs_json};
      const sourcesData = {sources_json};
      const scenarioData = {scenario_json};

      let gameState = {{
        round: 1,
        actionPoints: 2,
        transportProfile: "{initial_transport}",
        completedActions: [],
        history: [],
        status: "playing",
        outcome: null
      }};

      let previousRun = null;
      let map = null;
      let markers = {{}};

      function initMap() {{
        if (map) return;
        map = L.map('kc-map', {{
          center: [38.99, -94.54],
          zoom: 11,
          zoomControl: true,
          attributionControl: false
        }});

        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
          subdomains: 'abcd',
          maxZoom: 19
        }}).addTo(map);

        // Add markers
        locationsData.features.forEach(f => {{
          const [lon, lat] = f.geometry.coordinates;
          const isMcc = f.id === 'mcc-penn-valley-hsi';
          const markerColor = isMcc ? '#818cf8' : (f.id === 'ruskin-high' ? '#38bdf8' : '#34d399');

          const customIcon = L.divIcon({{
            className: 'kc-custom-marker',
            html: `<div style="background: ${{markerColor}}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid #ffffff; box-shadow: 0 0 10px ${{markerColor}};"></div>`,
            iconSize: [14, 14],
            iconAnchor: [7, 7]
          }});

          const marker = L.marker([lat, lon], {{ icon: customIcon }}).addTo(map);
          marker.bindPopup(`
            <div style="font-family: sans-serif; font-size: 0.8rem;">
              <strong style="color: #38bdf8;">${{f.properties.name}}</strong><br/>
              <span style="color: #94a3b8;">${{f.properties.category_label}}</span><br/>
              <p style="margin-top: 4px; color: #cbd5e1;">${{f.properties.address}}</p>
            </div>
          `);
          marker.on('click', () => selectLocation(f.id));
          markers[f.id] = marker;
        }});
      }}

      window.selectLocation = function(locId) {{
        const feat = locationsData.features.find(f => f.id === locId);
        if (!feat) return;
        document.getElementById('kc-focus-badge').innerText = feat.properties.name;
        document.getElementById('kc-focus-desc').innerText = feat.properties.description;
        map.panTo([feat.geometry.coordinates[1], feat.geometry.coordinates[0]], {{ animate: true, duration: 0.8 }});
      }};

      function showStartModal() {{
        const overlay = document.getElementById('kc-modal-overlay');
        const box = document.getElementById('kc-modal-box');
        overlay.style.display = 'flex';
        box.innerHTML = `
          <div style="border-bottom: 1px solid #334155; padding-bottom: 12px;">
            <span class="kc-source-tag">Mission 01 · Fictional Scenario</span>
            <h2 style="font-size: 1.25rem; color: #38bdf8; margin-top: 6px;">A Future in Healthcare</h2>
            <p style="font-size: 0.85rem; color: #94a3b8;">Ruskin High School · Grade 10 · Hickman Mills C-1</p>
          </div>
          <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
            You are a 10th-grade student exploring healthcare careers. Your challenge is to navigate real Kansas City opportunities, balance competing time priorities, and assemble an actionable pathway inquiry plan over 3 planning rounds.
          </p>
          <div style="background: #0f172a; padding: 14px; border-radius: 8px; border: 1px solid #334155;">
            <label style="font-size: 0.8rem; font-weight: 700; color: #f8fafc; display: block; margin-bottom: 8px;">
              Select Starting Transportation Circumstance:
            </label>
            <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.78rem;">
              <label style="display: flex; align-items: flex-start; gap: 8px; cursor: pointer;">
                <input type="radio" name="kc_transport_radio" value="reliable" ${{gameState.transportProfile === 'reliable' ? 'checked' : ''}} style="margin-top: 2px;">
                <div>
                  <strong style="color: #38bdf8;">Reliable Transportation</strong>
                  <div style="color: #94a3b8;">You have dependable personal/family transport for off-campus programs. Standard pathway requirements.</div>
                </div>
              </label>
              <label style="display: flex; align-items: flex-start; gap: 8px; cursor: pointer;">
                <input type="radio" name="kc_transport_radio" value="needs-coordination" ${{gameState.transportProfile === 'needs-coordination' ? 'checked' : ''}} style="margin-top: 2px;">
                <div>
                  <strong style="color: #fbbf24;">Transportation Needs Coordination</strong>
                  <div style="color: #94a3b8;">You rely on shuttles or RideKC transit. Off-campus programs require an extra 1-AP logistics investigation.</div>
                </div>
              </label>
            </div>
          </div>
          <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 8px;">
            <button class="kc-btn kc-btn-primary" style="padding: 8px 18px; font-size: 0.85rem;" onclick="handleStartGame()">
              Start Planning Mission →
            </button>
          </div>
        `;
      }}

      window.handleStartGame = function() {{
        const selected = document.querySelector('input[name="kc_transport_radio"]:checked');
        if (selected) {{
          gameState.transportProfile = selected.value;
        }}
        document.getElementById('kc-modal-overlay').style.display = 'none';
        initMap();
        updateUI();
      }};

      function updateUI() {{
        // Badges
        document.getElementById('kc-round-badge').innerText = `Round ${{gameState.round}} of 3`;
        document.getElementById('kc-ap-badge').innerText = `${{gameState.actionPoints}} AP Available`;
        document.getElementById('kc-transport-badge').innerText = gameState.transportProfile === 'reliable' 
          ? '🚗 Transport: Reliable' 
          : '🚌 Transport: Needs Coordination';
        document.getElementById('kc-advance-btn').innerText = gameState.round === 3 ? 'Finish Mission 🏁' : `End Round ${{gameState.round}} →`;
        document.getElementById('kc-round-timer').innerText = `${{gameState.actionPoints}} AP remaining this round`;

        // Render Action Cards
        renderActionCards();
        renderHistory();
      }}

      function isActionUnlocked(a) {{
        if (gameState.status !== 'playing') return false;
        if (gameState.completedActions.includes(a.id)) return false;
        if (gameState.round < a.round_available) return false;

        for (let req of a.requires) {{
          if (!gameState.completedActions.includes(req)) {{
            // check result flags
            const match = scenarioData.scenario.actions.find(act => act.result_flag === req && gameState.completedActions.includes(act.id));
            if (!match) return false;
          }}
        }}

        if (a.requires_transport_profile && gameState.transportProfile !== a.requires_transport_profile) {{
          return false;
        }}

        if (a.requires_transport_investigation && gameState.transportProfile === 'needs-coordination') {{
          if (!gameState.completedActions.includes('investigate_transport')) return false;
        }}

        return true;
      }}

      function renderActionCards() {{
        const container = document.getElementById('kc-actions-list');
        container.innerHTML = '';

        const allActions = scenarioData.scenario.actions;
        allActions.forEach(a => {{
          const isDone = gameState.completedActions.includes(a.id);
          const unlocked = isActionUnlocked(a);
          const canAfford = gameState.actionPoints >= a.cost_ap;

          if (!unlocked && !isDone) {{
            // If action is round-locked, show placeholder or skip
            if (gameState.round < a.round_available) return;
            // If action is transport-profile specific and doesn't match, hide it
            if (a.requires_transport_profile && gameState.transportProfile !== a.requires_transport_profile) return;
          }}

          const loc = locationsData.features.find(f => f.id === a.location_id);
          const locName = loc ? loc.properties.name : 'Kansas City';

          const card = document.createElement('div');
          card.className = `kc-action-card ${{isDone ? 'completed' : ''}}`;
          card.innerHTML = `
            <div class="kc-action-header">
              <span class="kc-action-title">${{isDone ? '✓ ' : ''}}${{a.title}}</span>
              <span class="kc-action-cost">${{a.cost_ap}} AP</span>
            </div>
            <div class="kc-action-desc">${{a.description}}</div>
            <div class="kc-action-meta">
              <span class="kc-loc-tag" onclick="selectLocation('${{a.location_id}}')" style="cursor: pointer;" title="Show on map">
                📍 ${{locName}}
              </span>
              <div style="display: flex; gap: 6px;">
                <button class="kc-btn kc-btn-outline" style="padding: 4px 8px; font-size: 0.7rem;" onclick="openEvidenceDrawer('${{a.id}}')">
                  Why?
                </button>
                <button class="kc-btn kc-btn-primary" 
                  ${{!unlocked || !canAfford || isDone ? 'disabled' : ''}} 
                  onclick="handleTakeAction('${{a.id}}')">
                  ${{isDone ? 'Done' : (unlocked && !canAfford ? 'Need AP' : 'Take Action')}}
                </button>
              </div>
            </div>
          `;
          container.appendChild(card);
        }});
      }}

      function renderHistory() {{
        const container = document.getElementById('kc-history-list');
        if (gameState.history.length === 0) {{
          container.innerHTML = '<div style="color: #64748b; font-style: italic; font-size: 0.75rem;">No actions completed yet.</div>';
          return;
        }}
        container.innerHTML = '';
        gameState.history.slice().reverse().forEach(h => {{
          const item = document.createElement('div');
          item.className = 'kc-history-item';
          item.innerHTML = `
            <div style="display: flex; justify-content: space-between; font-weight: 600; font-size: 0.75rem; color: #38bdf8; margin-bottom: 2px;">
              <span>Round ${{h.round}}: ${{h.action_title}}</span>
              <span style="color: #94a3b8;">${{h.ap_remaining}} AP left</span>
            </div>
            <div style="color: #e2e8f0; font-size: 0.74rem;">${{h.message}}</div>
          `;
          container.appendChild(item);
        }});
      }}

      window.handleTakeAction = function(actionId) {{
        const action = scenarioData.scenario.actions.find(a => a.id === actionId);
        if (!action) return;

        if (gameState.actionPoints < action.cost_ap) return;

        gameState.actionPoints -= action.cost_ap;
        gameState.completedActions.push(action.id);
        gameState.history.push({{
          round: gameState.round,
          action_id: action.id,
          action_title: action.title,
          ap_remaining: gameState.actionPoints,
          message: action.outcome_message
        }});

        selectLocation(action.location_id);
        updateUI();
      }};

      window.handleAdvanceRound = function() {{
        if (gameState.round < 3) {{
          gameState.round += 1;
          gameState.actionPoints = 2; // Unspent AP expires
          if (gameState.round === 2) {{
            // Discover MCC
            selectLocation('mcc-penn-valley-hsi');
          }}
          updateUI();
        }} else {{
          // End of game
          gameState.status = 'finished';
          gameState.actionPoints = 0;
          evaluateAndShowOutcome();
        }}
      }};

      function evaluateAndShowOutcome() {{
        let outcomeId = 'still_exploring';
        if (gameState.completedActions.includes('prepare_health_start_inquiry')) {{
          outcomeId = 'health_start_prepared';
        }} else if (gameState.completedActions.includes('draft_postgrad_plan')) {{
          outcomeId = 'postgrad_plan_prepared';
        }}
        const outcome = scenarioData.scenario.endings[outcomeId];
        gameState.outcome = outcome;

        const overlay = document.getElementById('kc-modal-overlay');
        const box = document.getElementById('kc-modal-box');
        overlay.style.display = 'flex';

        let comparisonHtml = '';
        if (previousRun) {{
          comparisonHtml = `
            <div style="background: #090d16; border: 1px solid #334155; border-radius: 8px; padding: 12px; margin-top: 8px;">
              <h4 style="font-size: 0.8rem; color: #f8fafc; margin-bottom: 6px;">Side-by-Side Run Comparison</h4>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.75rem;">
                <div>
                  <strong style="color: #94a3b8;">Previous Run (${{previousRun.transportProfile}}):</strong>
                  <div style="color: #cbd5e1; margin-top: 2px;">${{previousRun.outcome.title}}</div>
                  <div style="color: #64748b;">${{previousRun.completedActions.length}} actions completed</div>
                </div>
                <div>
                  <strong style="color: #38bdf8;">Current Run (${{gameState.transportProfile}}):</strong>
                  <div style="color: #cbd5e1; margin-top: 2px;">${{outcome.title}}</div>
                  <div style="color: #64748b;">${{gameState.completedActions.length}} actions completed</div>
                </div>
              </div>
            </div>
          `;
        }}

        box.innerHTML = `
          <div style="border-bottom: 1px solid #334155; padding-bottom: 12px;">
            <span class="kc-source-tag" style="background: #0369a1; color: #e0f2fe;">${{outcome.status_badge}}</span>
            <h2 style="font-size: 1.2rem; color: #38bdf8; margin-top: 6px;">${{outcome.title}}</h2>
            <p style="font-size: 0.82rem; color: #94a3b8;">Transport: ${{gameState.transportProfile}} · 3 Rounds Completed</p>
          </div>
          <p style="font-size: 0.82rem; color: #f1f5f9; line-height: 1.45;">
            ${{outcome.description}}
          </p>
          <div style="background: #0f172a; padding: 12px; border-radius: 8px; border-left: 3px solid #38bdf8; font-size: 0.78rem;">
            <strong style="color: #38bdf8; display: block; margin-bottom: 4px;">Real-World Takeaway:</strong>
            ${{outcome.real_world_takeaway}}
          </div>
          <div style="font-size: 0.78rem; color: #94a3b8;">
            <strong style="color: #cbd5e1; display: block; margin-bottom: 4px;">Questions Still Requiring Confirmation:</strong>
            <ul style="padding-left: 18px; line-height: 1.4;">
              ${{outcome.unanswered_questions.map(q => `<li>${{q}}</li>`).join('')}}
            </ul>
          </div>
          ${{comparisonHtml}}
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
            <span style="font-size: 0.75rem; color: #64748b;">No demographic predictions fabricated.</span>
            <button class="kc-btn kc-btn-primary" style="padding: 8px 18px;" onclick="handleReplay()">
              Replay / Change Circumstances ↺
            </button>
          </div>
        `;
      }}

      window.handleReplay = function() {{
        previousRun = JSON.parse(JSON.stringify(gameState));
        const alternateTransport = gameState.transportProfile === 'reliable' ? 'needs-coordination' : 'reliable';
        gameState = {{
          round: 1,
          actionPoints: 2,
          transportProfile: alternateTransport,
          completedActions: [],
          history: [],
          status: "playing",
          outcome: null
        }};
        showStartModal();
      }}

      window.openEvidenceDrawer = function(contextId) {{
        const drawer = document.getElementById('kc-evidence-drawer');
        const content = document.getElementById('kc-drawer-content');
        drawer.classList.add('open');

        if (contextId === 'general') {{
          content.innerHTML = `
            <h4 style="color: #f8fafc; font-weight: 700;">Data Provenance & Sources</h4>
            <p>Every location and program constraint in KC Pathways is verified from official school and higher education sources:</p>
            ${{sourcesData.sources.map(s => `
              <div style="background: #1e293b; padding: 10px; border-radius: 6px; border: 1px solid #334155;">
                <div style="font-weight: 600; color: #38bdf8; font-size: 0.78rem;">${{s.title}}</div>
                <div style="color: #94a3b8; font-size: 0.72rem; margin: 2px 0;">${{s.organization}} · Checked ${{s.checked_date}}</div>
                <div style="color: #cbd5e1; font-size: 0.75rem;">${{s.notes}}</div>
                <a href="${{s.url}}" target="_blank" style="color: #38bdf8; font-size: 0.72rem; text-decoration: underline; margin-top: 4px; display: inline-block;">Official Source Link ↗</a>
              </div>
            `).join('')}}
          `;
        }} else {{
          const action = scenarioData.scenario.actions.find(a => a.id === contextId);
          const program = programsData.programs.find(p => p.id === 'health-start' || p.id === 'mcc-healthcare-pathway');
          content.innerHTML = `
            <h4 style="color: #f8fafc; font-weight: 700;">${{action ? action.title : 'Action Evidence'}}</h4>
            <span class="kc-source-tag">Verified Educational Record</span>
            <p>${{action ? action.description : ''}}</p>
            <div style="background: #1e293b; padding: 12px; border-radius: 6px; border: 1px solid #334155;">
              <strong style="color: #38bdf8; font-size: 0.78rem; display: block; margin-bottom: 4px;">Institutional Facts:</strong>
              <ul style="padding-left: 16px; font-size: 0.75rem; color: #cbd5e1; line-height: 1.45;">
                <li>District: Hickman Mills C-1</li>
                <li>Partner College: Metropolitan Community College</li>
                <li>Published Recruitment Period: January–April</li>
                <li>Credentials: CNA, Pharmacology Tech, Phlebotomy</li>
              </ul>
            </div>
            <div style="background: #182234; padding: 10px; border-radius: 6px; border: 1px solid #334155; font-size: 0.75rem;">
              <strong style="color: #fbbf24;">Explicitly Labeled Unknown:</strong>
              <p style="color: #94a3b8; margin-top: 2px;">
                Seat caps and specific bus routes for clinical off-campus placements vary annually and require direct counselor verification.
              </p>
            </div>
          `;
        }}
      }};

      window.closeEvidenceDrawer = function() {{
        document.getElementById('kc-evidence-drawer').classList.remove('open');
      }};

      // Initial execution
      showStartModal();
    }})();
  </script>
</div>
"""
    return HTML(html_code)
