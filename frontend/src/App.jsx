import React, { useState } from 'react';
import axios from 'axios';
import { 
  Bot, 
  Send, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  Terminal, 
  Github, 
  CloudSun, 
  Newspaper, 
  ArrowRight,
  BrainCircuit,
  Code2
} from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// --- Utility ---
function cn(...inputs) {
  return twMerge(clsx(inputs));
}

// --- Components ---

const StatusBadge = ({ status }) => {
  const styles = {
    idle: "bg-slate-100 text-slate-500 border-slate-200",
    planning: "bg-blue-50 text-blue-600 border-blue-200 animate-pulse",
    executing: "bg-purple-50 text-purple-600 border-purple-200 animate-pulse",
    verifying: "bg-amber-50 text-amber-600 border-amber-200 animate-pulse",
    success: "bg-emerald-50 text-emerald-600 border-emerald-200",
    error: "bg-red-50 text-red-600 border-red-200",
  };

  const labels = {
    idle: "Ready",
    planning: "Planning Task...",
    executing: "Executing Steps...",
    verifying: "Verifying Results...",
    success: "Completed Successfully",
    error: "Task Failed",
  };

  return (
    <div className={cn("px-3 py-1 rounded-full border text-xs font-medium flex items-center gap-2 transition-all", styles[status])}>
      {status === 'planning' && <BrainCircuit className="w-3 h-3" />}
      {status === 'executing' && <Terminal className="w-3 h-3" />}
      {status === 'verifying' && <CheckCircle2 className="w-3 h-3" />}
      {status === 'success' && <CheckCircle2 className="w-3 h-3" />}
      {status === 'error' && <AlertCircle className="w-3 h-3" />}
      {labels[status]}
    </div>
  );
};

const StepCard = ({ step, isCompleted, isCurrent }) => {
  const getIcon = (toolName) => {
    if (toolName.toLowerCase().includes('github')) return <Github className="w-4 h-4 text-slate-700" />;
    if (toolName.toLowerCase().includes('weather')) return <CloudSun className="w-4 h-4 text-blue-500" />;
    if (toolName.toLowerCase().includes('news')) return <Newspaper className="w-4 h-4 text-red-500" />;
    return <Code2 className="w-4 h-4 text-slate-500" />;
  };

  return (
    <div className={cn(
      "relative border rounded-lg p-4 transition-all duration-300",
      isCurrent ? "bg-white border-blue-400 shadow-md scale-[1.02]" : "bg-slate-50 border-slate-200",
      isCompleted ? "opacity-75" : "opacity-100"
    )}>
      <div className="flex items-start gap-3">
        <div className={cn(
          "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border",
          isCurrent ? "bg-blue-100 border-blue-300 text-blue-600" : "bg-white border-slate-200 text-slate-500"
        )}>
           {getIcon(step.tool)}
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <h4 className="text-sm font-semibold text-slate-800">Step {step.step_number}: {step.tool}</h4>
            {isCompleted && <span className="text-xs text-emerald-600 font-medium">Done</span>}
          </div>
          <p className="text-sm text-slate-600">{step.description}</p>
          <div className="mt-2 text-xs bg-slate-100 p-2 rounded border border-slate-200 font-mono text-slate-500 overflow-x-auto">
            {JSON.stringify(step.parameters)}
          </div>
        </div>
      </div>
    </div>
  );
};

const ResultViewer = ({ data, summary }) => {
  return (
    <div className="mt-6 space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 flex items-center gap-2">
          <Bot className="w-4 h-4 text-indigo-500" />
          <h3 className="font-semibold text-slate-800">Agent Summary</h3>
        </div>
        <div className="p-4 text-slate-700 leading-relaxed">
          {summary}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
             <div className="bg-slate-50 px-4 py-2 border-b border-slate-200">
                <code className="text-xs text-slate-500 font-mono">{key}</code>
             </div>
             <div className="p-4 bg-slate-50/50 overflow-x-auto">
                <pre className="text-xs font-mono text-slate-600">
                  {JSON.stringify(value, null, 2)}
                </pre>
             </div>
          </div>
        ))}
      </div>
    </div>
  );
};

function App() {
  const [task, setTask] = useState("");
  const [status, setStatus] = useState('idle');
  const [plan, setPlan] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!task.trim()) return;

    setStatus('planning');
    setPlan(null);
    setResult(null);
    setError(null);

    try {
      // Simulate phases for better UX (since backend does it all in one go currently)
      // Ideally backend would stream events, but we'll fake the progress for now
      // or just show "Processing"
      
      const response = await axios.post('http://localhost:8000/task', { task });
      
      const data = response.data;
      
      // If we had the plan separately, we'd show it. 
      // The backend returns everything at once, so we just show the final state.
      setPlan(data.plan);
      setResult(data);
      
      if (data.status === 'success') {
        setStatus('success');
      } else {
         setStatus('error');
         setError(data.errors?.join(', ') || "Unknown error occurred");
      }

    } catch (err) {
      console.error(err);
      setStatus('error');
      setError(err.response?.data?.detail || "Failed to connect to agent backend");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-indigo-100 selection:text-indigo-900">
      <div className="max-w-3xl mx-auto px-6 py-12">
        
        {/* Header */}
        <header className="mb-12 text-center">
          <div className="inline-flex items-center justify-center p-3 bg-white rounded-2xl shadow-sm border border-slate-200 mb-4">
            <Bot className="w-8 h-8 text-indigo-600" />
          </div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">AI Operations Agent</h1>
          <p className="text-slate-500 text-lg">Your autonomous assistant for GitHub, News, and more.</p>
        </header>

        {/* Input Area */}
        <form onSubmit={handleSubmit} className="mb-8 relative">
          <div className="relative group">
            <input
              type="text"
              value={task}
              onChange={(e) => setTask(e.target.value)}
              placeholder="Describe your task..."
              className="w-full px-6 py-4 pr-16 text-lg bg-white rounded-2xl shadow-sm border border-slate-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 outline-none transition-all placeholder:text-slate-400"
              disabled={status === 'planning' || status === 'executing' || status === 'verifying'}
            />
            <button
              type="submit"
              disabled={!task.trim() || status !== 'idle' && status !== 'success' && status !== 'error'}
              className="absolute right-2 top-2 bottom-2 aspect-square bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl flex items-center justify-center transition-colors shadow-sm"
            >
              {status === 'idle' || status === 'success' || status === 'error' ? (
                <Send className="w-5 h-5" />
              ) : (
                <Loader2 className="w-5 h-5 animate-spin" />
              )}
            </button>
          </div>
          {error && (
            <div className="absolute top-full mt-2 left-0 right-0 flex items-center justify-center gap-2 text-red-600 text-sm font-medium animate-in fade-in slide-in-from-top-1">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}
        </form>

        {/* Status Area */}
        <div className="flex justify-center mb-8">
           <StatusBadge status={status} />
        </div>

        {/* Content Area */}
        <div className="space-y-8 pb-20">
          
          {/* Plan Section */}
          {plan && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 ease-out">
              <div className="flex items-center gap-2 mb-4">
                 <BrainCircuit className="w-5 h-5 text-indigo-500" />
                 <h2 className="text-lg font-semibold text-slate-800">Execution Plan</h2>
              </div>
              
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-1 space-y-2">
                 {/* Summary */}
                 <div className="px-5 py-4 border-b border-slate-100">
                    <p className="text-slate-600 italic">"{plan.task_summary}"</p>
                 </div>

                 {/* Steps */}
                 <div className="p-4 space-y-3 bg-slate-50/50 rounded-xl">
                   {plan.steps.map((step, idx) => (
                     <StepCard 
                        key={idx} 
                        step={step} 
                        isCompleted={true} // Since we get full response, all are done
                        isCurrent={false}
                     />
                   ))}
                 </div>
              </div>
            </div>
          )}

          {/* Results Section */}
          {result && (
            <div className="animate-in fade-in slide-in-from-bottom-8 duration-700 ease-out delay-150">
               <ResultViewer data={result.data} summary={result.summary} />
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default App;
