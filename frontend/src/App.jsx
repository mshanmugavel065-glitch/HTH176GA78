import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import HeroLanding from './components/HeroLanding';
import ChatInterface from './components/ChatInterface';
import DisasterIntelligencePanel from './components/DisasterIntelligencePanel';
import SimulatedRegionMap from './components/SimulatedRegionMap';
import AgentNetwork from './components/AgentNetwork';
import ResourcePanel from './components/ResourcePanel';
import ZoneCard from './components/ZoneCard';
import AgentActivity from './components/AgentActivity';
import ResponsePlan from './components/ResponsePlan';
import BeforeAfterComparison from './components/BeforeAfterComparison';
import ConflictPanel from './components/ConflictPanel';
import PublicAlertPanel from './components/PublicAlertPanel';
import DecisionExplanation from './components/DecisionExplanation';
import DemoControls from './components/DemoControls';

import {
  fetchSystemState,
  analyzeSituation,
  sendChatMessage,
  triggerPlan,
  triggerReplan,
  addPresetZoneD,
  deleteZone,
  resetSystem,
  simulateHazardUpdate
} from './services/api';

export default function App() {
  const [systemState, setSystemState] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeAgent, setActiveAgent] = useState(null);
  const [demoStep, setDemoStep] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');

  // Initial fetch
  useEffect(() => {
    loadState();
  }, []);

  const loadState = async () => {
    try {
      const state = await fetchSystemState();
      setSystemState(state);
    } catch (err) {
      console.error('Error fetching system state:', err);
    }
  };

  const handleAnalyzeSituation = async (location, situation) => {
    setIsProcessing(true);
    setStatusMessage('Mapping synthetic region topology & disaster sectors...');
    try {
      const newState = await analyzeSituation(location, situation);
      setSystemState(newState);
      setStatusMessage('Analysis complete.');
    } catch (err) {
      console.error('Error analyzing situation:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSendMessage = async (userText) => {
    setIsProcessing(true);
    setStatusMessage('Core agents analyzing request...');
    try {
      const newState = await sendChatMessage(userText);
      setSystemState(newState);
      setStatusMessage('Response ready.');
    } catch (err) {
      console.error('Error sending chat message:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRunPlan = async () => {
    setIsProcessing(true);
    setStatusMessage('Executing Disaster Intelligence, Medical, Logistics, and Communications agents...');
    try {
      const newState = await triggerPlan();
      setSystemState(newState);
    } catch (err) {
      console.error('Error running plan:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAddZoneD = async () => {
    setIsProcessing(true);
    setStatusMessage('⚠️ Adding Zone D (Hospital Landslide & Flood Hazard)...');
    try {
      const newState = await addPresetZoneD();
      setSystemState(newState);
      setStatusMessage('Zone D added to crisis map. Ready for Re-Planning.');
    } catch (err) {
      console.error('Error adding Zone D:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSimulateHazardUpdate = async () => {
    setIsProcessing(true);
    setStatusMessage('🌧️ Surge telemetry update: +50mm rainfall...');
    try {
      const newState = await simulateHazardUpdate(50.0, 0.5);
      setSystemState(newState);
      setStatusMessage('Hazard telemetry updated. Ready for Re-Planning.');
    } catch (err) {
      console.error('Error simulating hazard update:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReplan = async () => {
    setIsProcessing(true);
    setStatusMessage('Re-running 5-agent pipeline and enforcing fixed resource bounds...');
    try {
      const newState = await triggerReplan();
      setSystemState(newState);
    } catch (err) {
      console.error('Error replanning:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDeleteZone = async (zoneId) => {
    try {
      const newState = await deleteZone(zoneId);
      setSystemState(newState);
    } catch (err) {
      console.error('Error deleting zone:', err);
    }
  };

  const handleReset = async () => {
    setIsProcessing(true);
    setDemoStep(0);
    setStatusMessage('Resetting system state...');
    try {
      const newState = await resetSystem();
      setSystemState(newState);
      setStatusMessage('Reset complete.');
    } catch (err) {
      console.error('Error resetting system:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  // Guided One-Click Response Simulation Workflow
  const handleStartAutoDemo = async () => {
    if (!systemState?.location) {
      await handleAnalyzeSituation('Coimbatore, Tamil Nadu', 'Heavy rainfall causing flooding across multiple residential and industrial sectors.');
    }
    setDemoStep(1);
    setIsProcessing(true);
    setStatusMessage('SIMULATION STEP 1: Running Disaster Intelligence & initial flood response planning...');
    const planState = await triggerPlan();
    setSystemState(planState);
    await new Promise(r => setTimeout(r, 1200));

    setDemoStep(2);
    setStatusMessage('SIMULATION STEP 2: Disaster Intelligence & Medical Triage evaluating critical trauma density...');
    await new Promise(r => setTimeout(r, 1200));

    setDemoStep(3);
    setStatusMessage('SIMULATION STEP 3: ⚠️ NEW DISASTER ZONE DETECTED! Adding Zone D (Hospital Landslide)...');
    const addedState = await addPresetZoneD();
    setSystemState(addedState);
    await new Promise(r => setTimeout(r, 1400));

    setDemoStep(4);
    setStatusMessage('SIMULATION STEP 4: Triggering Dynamic Re-planning & Hard Resource Constraint Solver...');
    const replanState = await triggerReplan();
    setSystemState(replanState);
    await new Promise(r => setTimeout(r, 1000));

    setDemoStep(5);
    setStatusMessage('SIMULATION STEP 5: Simulation Complete! Reviewing BEFORE → AFTER diffs & Public Alert draft.');
    setIsProcessing(false);
  };

  // Map allocations by zone ID
  const allocationsMap = {};
  if (systemState?.current_plan?.final_allocations) {
    systemState.current_plan.final_allocations.forEach(a => {
      allocationsMap[a.zone_id] = a;
    });
  }

  const isAnalyzed = Boolean(systemState?.is_analyzed && systemState?.location);

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-slate-950">
      
      {/* Header Bar */}
      <Header
        systemState={systemState}
        onReset={handleReset}
        isProcessing={isProcessing}
      />

      {/* Main Content Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-8">
        
        {/* HERO LANDING / INITIAL INPUT */}
        {!isAnalyzed ? (
          <HeroLanding
            onAnalyze={handleAnalyzeSituation}
            isProcessing={isProcessing}
          />
        ) : (
          <div className="space-y-8">
            
            {/* RESPONSE SIMULATION CONTROL BAR */}
            <DemoControls
              systemState={systemState}
              onRunPlan={handleRunPlan}
              onAddZoneD={handleAddZoneD}
              onReplan={handleReplan}
              onReset={handleReset}
              onSimulateHazardUpdate={handleSimulateHazardUpdate}
              isProcessing={isProcessing}
              onStartAutoDemo={handleStartAutoDemo}
              demoStep={demoStep}
              onUploadComplete={(newState) => setSystemState(newState)}
            />

            {/* COMMANDER CHATBOT INTERFACE */}
            <ChatInterface
              chatHistory={systemState?.chat_history}
              onSendMessage={handleSendMessage}
              isProcessing={isProcessing}
              onActionClick={(act) => handleSendMessage(act)}
            />

            {/* DISASTER INTELLIGENCE & SEVERITY ASSESSMENT DASHBOARD */}
            <DisasterIntelligencePanel systemState={systemState} />

            {/* COMMAND-CENTER DASHBOARD SECTION */}
            <div className="pt-6 border-t border-slate-800 space-y-8">
              
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <h2 className="text-base font-bold text-white uppercase tracking-wider font-mono">
                    Situation Command Center — {systemState?.location}
                  </h2>
                  <p className="text-xs text-slate-400">
                    RESQ-AI Multi-Agent Response Coordination & Resource Constraint Solver
                  </p>
                </div>
                <span className="text-xs text-slate-400 font-mono bg-slate-800 px-3 py-1 rounded border border-slate-700">
                  Fixed Limits: 5 Vehicles | 10 Medics | 3 Shelters | 100 Supplies
                </span>
              </div>

              {/* Simulated Region Map & Road Network */}
              <SimulatedRegionMap
                zones={systemState?.zones}
                allocations={systemState?.current_plan?.final_allocations}
              />

              {/* Multi-Agent Collaboration Network */}
              <AgentNetwork
                systemState={systemState}
                isProcessing={isProcessing}
                activeAgent={activeAgent}
              />

              {/* Resource Inventory Meters */}
              <ResourcePanel systemState={systemState} />

              {/* Active Disaster Sectors */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                    Active Disaster Sectors ({systemState?.zones?.length || 0})
                  </h3>
                  <span className="text-xs text-slate-400 font-mono">Telemetry Telemetry</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {systemState?.zones?.map(zone => (
                    <ZoneCard
                      key={zone.id}
                      zone={zone}
                      allocation={allocationsMap[zone.id]}
                      onDelete={handleDeleteZone}
                    />
                  ))}
                </div>
              </div>

              {/* Multi-Agent Conflict Resolution Matrix */}
              <ConflictPanel plan={systemState?.current_plan} />

              {/* Response Plan Table & Activity Feed */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <ResponsePlan plan={systemState?.current_plan} />
                </div>
                <div className="lg:col-span-1">
                  <AgentActivity logs={systemState?.agent_activity} />
                </div>
              </div>

              {/* BEFORE vs AFTER Dynamic Re-planning Differential */}
              <BeforeAfterComparison
                previousPlan={systemState?.previous_plan}
                currentPlan={systemState?.current_plan}
                differences={systemState?.plan_differences}
              />

              {/* Draft Public Evacuation Alert */}
              <PublicAlertPanel alert={systemState?.current_plan?.public_alert} />

              {/* Decision Rationale & Trade-offs */}
              <DecisionExplanation
                plan={systemState?.current_plan}
                systemState={systemState}
              />

            </div>

          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950 py-4 px-6 text-center text-xs text-slate-500 font-mono">
        RESQ-AI — Rapid Emergency Support & Coordination — AI • Multi-Agent Response Platform
      </footer>

    </div>
  );
}
