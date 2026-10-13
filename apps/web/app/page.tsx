"use client";

import { useCallback, useEffect, useState } from "react";
import { Activity, ArrowUpRight, BrainCircuit, Check, CircleHelp, Code2, Cpu, GitBranch, LayoutGrid, Network, Play, Plus, RefreshCw, Shield, Square, Terminal, Trash2, X } from "lucide-react";

const API = process.env.NEXT_PUBLIC_AGENTOS_API_URL ?? "http://127.0.0.1:8000";
type Agent = { id: string; name: string; description: string; instructions: string; is_preset: number };
type Task = { id: string; title: string; description: string; agent_id: string; status: string; result: string | null; created_at: string };
type Memory = { id: string; scope: string; agent_id: string | null; content: string };
type SystemInfo = { runtime: string; model_configured: boolean; capabilities: string[] };
type View = "universe" | "tasks" | "memory" | "studio";
const stations = [[53,21],[72,30],[79,57],[62,74],[37,75],[22,56],[29,29],[50,50],[86,18],[14,80],[86,81],[15,15]];
const symbols = ["◈", "✦", "⌘", "◉", "⊙", "◇", "⬡", "✧", "⌁"];

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, { ...options, headers: { "Content-Type": "application/json", ...(options?.headers ?? {}) }, cache: "no-store" });
  if (!response.ok) {
    const problem = await response.json().catch(() => null);
    throw new Error(typeof problem?.detail === "string" ? problem.detail : `Request failed (${response.status})`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export default function Home() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [system, setSystem] = useState<SystemInfo | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [view, setView] = useState<View>("universe");
  const [taskTitle, setTaskTitle] = useState("");
  const [taskDescription, setTaskDescription] = useState("");
  const [memoryText, setMemoryText] = useState("");
  const [addingAgent, setAddingAgent] = useState(false);
  const [agentName, setAgentName] = useState("");
  const [agentInstructions, setAgentInstructions] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [selectedTask, setSelectedTask] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [a, t, m, s] = await Promise.all([
        api<Agent[]>("/api/v1/agents"), api<Task[]>("/api/v1/tasks"),
        api<Memory[]>("/api/v1/memories"), api<SystemInfo>("/api/v1/system"),
      ]);
      setAgents(a); setTasks(t); setMemories(m); setSystem(s);
      setSelectedAgent(old => old && a.some(x => x.id === old) ? old : (a[0]?.id ?? null));
      setError("");
    } catch (err) { setError(err instanceof Error ? err.message : "Backend unavailable"); }
  }, []);
  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => { const id = setInterval(() => { void refresh(); }, 5000); return () => clearInterval(id); }, [refresh]);

  const chosen = agents.find(a => a.id === selectedAgent);
  const chosenTask = tasks.find(t => t.id === selectedTask);
  const tasksForAgent = tasks.filter(t => t.agent_id === selectedAgent);
  async function act(fn: () => Promise<void>) {
    setBusy(true); setError(""); setMessage("");
    try { await fn(); await refresh(); }
    catch (err) { setError(err instanceof Error ? err.message : "Unknown error"); }
    finally { setBusy(false); }
  }
  async function createTask() {
    if (!selectedAgent) return;
    await act(async () => {
      const task = await api<Task>("/api/v1/tasks", { method: "POST", body: JSON.stringify({ title: taskTitle, description: taskDescription, agent_id: selectedAgent }) });
      setSelectedTask(task.id); setTaskTitle(""); setTaskDescription(""); setMessage("Task added to queue");
    });
  }
  async function createAgent() {
    await act(async () => {
      const result = await api<Agent>("/api/v1/agents", { method: "POST", body: JSON.stringify({ name: agentName, description: "Custom specialist agent", instructions: agentInstructions }) });
      setSelectedAgent(result.id); setAddingAgent(false); setAgentName(""); setAgentInstructions(""); setMessage("Custom agent created");
    });
  }
  async function createMemory() {
    await act(async () => {
      await api("/api/v1/memories", { method: "POST", body: JSON.stringify({ scope: "project", content: memoryText }) });
      setMemoryText(""); setMessage("Project note saved");
    });
  }
  async function runTask(id: string) { await act(async () => { await api(`/api/v1/tasks/${id}/run`, { method: "POST" }); setMessage("Model response saved"); }); }
  async function cancelTask(id: string) { await act(async () => { await api(`/api/v1/tasks/${id}/cancel`, { method: "POST" }); setMessage("Task cancelled"); }); }
  async function deleteMemory(id: string) { await act(async () => { await api(`/api/v1/memories/${id}`, { method: "DELETE" }); setMessage("Memory removed"); }); }

  return <main className="shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">A<span className="brand-dot">.</span></span><span>AGENT<span className="muted">OS</span></span></div>
      <p className="nav-heading">WORKSPACE</p>
      <nav aria-label="Main navigation">
        <button className={view === "universe" ? "nav-item active" : "nav-item"} onClick={() => setView("universe")}><Network size={17}/> Agent Universe</button>
        <button className={view === "tasks" ? "nav-item active" : "nav-item"} onClick={() => setView("tasks")}><Activity size={17}/> Missions <span className="nav-count">{tasks.length}</span></button>
        <button className={view === "memory" ? "nav-item active" : "nav-item"} onClick={() => setView("memory")}><BrainCircuit size={17}/> Memory <span className="nav-count">{memories.length}</span></button>
        <button className={view === "studio" ? "nav-item active" : "nav-item"} onClick={() => setView("studio")}><Code2 size={17}/> Code Studio <span className="soon">NEXT</span></button>
      </nav>
      <p className="nav-heading second">YOUR AGENTS</p>
      <div className="agent-list">{agents.map((agent, i) => <button key={agent.id} onClick={() => {setSelectedAgent(agent.id);setView("universe");}} className={agent.id === selectedAgent && view === "universe" ? "agent-link selected" : "agent-link"}><span className="agent-avatar">{symbols[i % symbols.length]}</span><span>{agent.name}</span><span className="agent-indicator"/></button>)}</div>
      <button className="new-agent" onClick={() => {setAddingAgent(true);setView("universe");}}><Plus size={16}/> Create custom agent</button>
      <div className="sidebar-bottom"><span className="state-dot"/> LOCAL DEVELOPMENT <span className="version">v0.1</span></div>
    </aside>

    <section className="center-panel">
      <header className="topbar"><div className="breadcrumb">PERSONAL WORKSPACE <span>/</span> <strong>{view === "universe" ? "AGENT UNIVERSE" : view.toUpperCase()}</strong></div><div className="top-actions"><div className="connection-status"><span className={system ? "state-dot" : "state-dot offline"}/>{system ? (system.model_configured ? "MODEL CONNECTED" : "MODEL SETUP NEEDED") : "OFFLINE"}</div><button className="icon-button" aria-label="Refresh data" title="Refresh data" onClick={() => void refresh()}><RefreshCw size={16}/></button></div></header>
      {error && <div role="alert" className="error-message"><CircleHelp size={16}/><span>{error}{!system ? " — start the API on 127.0.0.1:8000" : ""}</span><button aria-label="Dismiss error" onClick={() => setError("")}><X size={14}/></button></div>}
      {message && <div className="success-message"><Check size={14}/>{message}</div>}
      {view === "universe" && <>
        <div className="section-title"><div><div className="eyebrow">THE CONTROL PLANE</div><h1>Agent Universe<span className="title-star">✧</span></h1><p>Every node is a real agent. Select one to assign a mission.</p></div><span className="room-live"><span className="state-dot"/> {agents.length} REGISTERED AGENTS</span></div>
        <div className="universe" aria-label="Agent universe visualization">
          <div className="universe-grid"/>
          <svg className="connections" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
            {agents.map((agent, i) => <line key={agent.id} x1="50" y1="50" x2={stations[i % stations.length][0]} y2={stations[i % stations.length][1]} stroke={selectedAgent === agent.id ? "#75aaff" : "#36526d"} strokeWidth={selectedAgent === agent.id ? ".3" : ".12"} vectorEffect="non-scaling-stroke" opacity={selectedAgent === agent.id ? ".9" : ".65"}/>)}
          </svg>
          <div className="core-node"><span className="core-symbol">✺</span><span>AGENTOS</span></div>
          {agents.map((a, i) => {const [x, y] = stations[i % stations.length]; const count = tasks.filter(t => t.agent_id === a.id && t.status === "running").length;return <button key={a.id} aria-label={`Select ${a.name}`} title={`${a.name} · ${count ? "Running" : "Idle"}`} onClick={() => setSelectedAgent(a.id)} className={`graph-node ${selectedAgent === a.id ? "focused" : ""}`} style={{left:`${x}%`,top:`${y}%`}}><span className="node-orbit"><span className="node-symbol">{symbols[i % symbols.length]}</span></span><span className="node-label">{a.name}</span><span className="node-status">{count ? "RUNNING" : "IDLE"}</span></button>; })}
          <div className="graph-caption"><span className="graph-legend-dot"/> Live database agents <span className="legend-divider"/> Connected lines indicate registered agents</div>
          <div className="graph-coordinates">SYSTEM MAP // LOCAL SESSION</div>
        </div>
      </>}
      {view === "tasks" && <section className="content-view"><div className="eyebrow">MISSION CONTROL</div><h1>All Missions</h1><p>Queued, completed, or cancelled tasks from your local workspace.</p><div className="task-list">{tasks.length === 0 ? <div className="empty-state">No missions yet. Select an agent from the Universe to create one.</div> : tasks.map(t=><button className={selectedTask===t.id ? "task-row selected" : "task-row"} key={t.id} onClick={()=>setSelectedTask(t.id)}><span><b>{t.title}</b><small>{agents.find(a=>a.id===t.agent_id)?.name ?? "Unknown agent"} · {new Date(t.created_at).toLocaleString()}</small></span><span className={`task-status ${t.status}`}>{t.status.toUpperCase()}</span></button>)}</div></section>}
      {view === "memory" && <section className="content-view"><div className="eyebrow">PERSISTENT CONTEXT</div><h1>Memory Vault</h1><p>Visible, editable-by-deletion notes stored locally. Only approved notes are added here.</p><div className="memory-form"><textarea placeholder="Save a project decision, architecture rule, or useful instruction..." value={memoryText} onChange={e=>setMemoryText(e.target.value)}/><button className="primary-button" disabled={busy || memoryText.trim().length < 3} onClick={()=>void createMemory()}><Plus size={16}/> Save project note</button></div><div className="memory-list">{memories.map(m=><div key={m.id} className="memory-item"><BrainCircuit size={18}/><div><span className="memory-tag">{m.scope.toUpperCase()} MEMORY</span><p>{m.content}</p></div><button aria-label="Delete memory" title="Delete memory" onClick={()=>void deleteMemory(m.id)}><Trash2 size={16}/></button></div>)}{memories.length===0 && <div className="empty-state">No saved memories yet.</div>}</div></section>}
      {view === "studio" && <section className="content-view"><div className="eyebrow">DEVELOPMENT WORKSPACE</div><h1>Code Studio</h1><div className="feature-roadmap"><Code2 size={34}/><h2>Planned for the next milestone</h2><p>Monaco Editor, Git diffs, isolated terminals, test execution, live previews, Codex and Claude Code sessions. Not implemented in this starter.</p><div className="planned-items"><span><GitBranch size={14}/> Git worktrees</span><span><Terminal size={14}/> Isolated terminal</span><span><Shield size={14}/> Approval gates</span></div></div></section>}
      <footer className="center-footer"><span>AGENTOS / PROTOTYPE</span><span>LOCAL ONLY · NOT PRODUCTION READY</span></footer>
    </section>

    <aside className="detail-panel">
      <div className="detail-heading"><div><span className="eyebrow">INSPECTOR</span><h2>{addingAgent ? "Create agent" : chosen?.name ?? "Select an agent"}</h2></div><button className="icon-button" onClick={()=>setAddingAgent(!addingAgent)} aria-label="Toggle create agent"><Plus size={18}/></button></div>
      {addingAgent ? <div className="detail-content"><label>AGENT NAME<input placeholder="e.g. Security Analyst" value={agentName} onChange={e=>setAgentName(e.target.value)}/></label><label>SYSTEM INSTRUCTIONS<textarea placeholder="Describe exactly how this agent should behave..." value={agentInstructions} onChange={e=>setAgentInstructions(e.target.value)}/></label><button className="primary-button" disabled={busy || agentName.trim().length<2 || agentInstructions.trim().length<10} onClick={()=>void createAgent()}><Plus size={16}/> Create agent</button><button className="secondary-button" onClick={()=>setAddingAgent(false)}>Cancel</button></div> : chosen ? <div className="detail-content">
        <div className="agent-profile"><span className="big-avatar">◈</span><div><span className="tiny-label">SPECIALIST AGENT</span><h3>{chosen.name}</h3><span className="idle-chip"><span className="state-dot"/> AVAILABLE</span></div></div><p className="agent-description">{chosen.description}</p>
        <div className="divider"/><h4>ASSIGN A MISSION</h4><label>TASK NAME<input placeholder="Implement an API endpoint" value={taskTitle} onChange={e=>setTaskTitle(e.target.value)}/></label><label>INSTRUCTIONS<textarea placeholder="Describe exactly what the agent should work on..." value={taskDescription} onChange={e=>setTaskDescription(e.target.value)}/></label><button className="primary-button" disabled={busy || taskTitle.trim().length<2 || taskDescription.trim().length<3} onClick={()=>void createTask()}><Plus size={15}/> Queue new task</button>
        <div className="divider"/><div className="subhead"><h4>AGENT TASKS</h4><span>{tasksForAgent.length}</span></div>
        {tasksForAgent.length===0 ? <div className="small-empty">No tasks assigned yet.</div> : tasksForAgent.slice(0,8).map(t=><div className="mini-task" key={t.id}><button onClick={()=>setSelectedTask(selectedTask===t.id?null:t.id)}><span>{t.title}</span><small>{t.status}</small></button><div className="mini-actions">{t.status==="queued"&&<><button disabled={!system?.model_configured || busy} title={system?.model_configured ? "Run task" : "Configure model API key first"} onClick={()=>void runTask(t.id)}><Play size={14}/></button><button disabled={busy} title="Cancel queued task" onClick={()=>void cancelTask(t.id)}><Square size={12}/></button></>}</div></div>)}
      </div> : <div className="empty-state">Waiting for backend.</div>}
      {chosenTask && <div className="result-card"><div className="eyebrow">SELECTED MISSION</div><strong>{chosenTask.title}</strong><span className={`task-status ${chosenTask.status}`}>{chosenTask.status}</span><p>{chosenTask.result ?? "No model response yet."}</p></div>}
      <div className="right-bottom"><Cpu size={15}/><span>MODEL</span><b>{system?.model_configured ? "Configured" : "Not configured"}</b><ArrowUpRight size={13}/></div>
    </aside>
  </main>;
}
