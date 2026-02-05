import React, { useState } from 'react';
import axios from 'axios';
import Orb from './components/Orb';
import { 
  Bot, 
  Send,
  Forward, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  Terminal, 
  Github, 
  CloudSun, 
  Newspaper, 
  BrainCircuit,
  Code2,
  Lightbulb
} from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// --- Utility ---
function cn(...inputs) {
  return twMerge(clsx(inputs));
}

// --- Components ---



const QuickActionCard = ({ icon: Icon, title, description, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="group relative bg-white hover:bg-purple-50/50 rounded-2xl p-6 border border-slate-200 hover:border-purple-300 transition-all duration-300 hover:shadow-lg hover:-translate-y-1 text-left w-full"
    >
      <div className="flex items-start gap-4">
        <div className="p-3 rounded-xl bg-purple-100 group-hover:bg-purple-200 transition-colors">
          <Icon className="w-5 h-5 text-purple-600" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-slate-800 mb-1 group-hover:text-purple-900 transition-colors">
            {title}
          </h3>
          <p className="text-sm text-slate-500 leading-relaxed">
            {description}
          </p>
        </div>
      </div>
    </button>
  );
};

const MessageBubble = ({ type, content }) => {
  const isUser = type === 'user';
  
  return (
    <div className={cn(
      "flex gap-3 animate-fade-in-up",
      isUser ? "justify-end" : "justify-start"
    )}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-purple-300 flex items-center justify-center shrink-0">
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}
      <div className={cn(
        "max-w-[80%] rounded-2xl px-5 py-3",
        isUser 
          ? "bg-gradient-to-br from-purple-600 to-purple-500 text-white" 
          : "glass-card text-slate-800 border border-slate-200"
      )}>
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-slate-500 to-slate-400 flex items-center justify-center shrink-0">
          <span className="text-white text-sm font-medium">U</span>
        </div>
      )}
    </div>
  );
};

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
    <div className={cn("px-3 py-1.5 rounded-full border text-xs font-medium flex items-center gap-2 transition-all", styles[status])}>
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
      isCurrent ? "bg-white border-purple-400 shadow-md scale-[1.02]" : "bg-slate-50 border-slate-200",
      isCompleted ? "opacity-75" : "opacity-100"
    )}>
      <div className="flex items-start gap-3">
        <div className={cn(
          "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border",
          isCurrent ? "bg-purple-100 border-purple-300 text-purple-600" : "bg-white border-slate-200 text-slate-500"
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
      <div className="glass-card rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 flex items-center gap-2">
          <Bot className="w-4 h-4 text-purple-500" />
          <h3 className="font-semibold text-slate-800">Agent Summary</h3>
        </div>
        <div className="p-4 text-slate-700 leading-relaxed">
          {summary}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="glass-card rounded-xl shadow-sm border border-slate-200 overflow-hidden">
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
  const [messages, setMessages] = useState([]);
  const [plan, setPlan] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const quickActions = [
    {
      icon: Github,
      title: "GitHub Operations",
      description: "Check repository stats, create issues, and manage PRs"
    },
    {
      icon: CloudSun,
      title: "Weather Information",
      description: "Get current weather and forecasts for any location"
    },
    {
      icon: Newspaper,
      title: "News Updates",
      description: "Fetch latest news on any topic or category"
    },
    {
      icon: Lightbulb,
      title: "Custom Task",
      description: "Run any automated task or workflow"
    }
  ];

  const handleQuickAction = (action) => {
    setTask(action.description);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!task.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { type: 'user', content: task }]);
    
    setStatus('planning');
    setPlan(null);
    setResult(null);
    setError(null);
    
    const currentTask = task;
    setTask(""); // Clear input

    try {
      const response = await axios.post('http://localhost:8000/task', { task: currentTask });
      const data = response.data;
      
      setPlan(data.plan);
      setResult(data);
      
      // Add agent response
      setMessages(prev => [...prev, { 
        type: 'agent', 
        content: data.summary || "Task completed successfully!" 
      }]);
      
      if (data.status === 'success') {
        setStatus('success');
      } else {
         setStatus('error');
         setError(data.errors?.join(', ') || "Unknown error occurred");
      }

    } catch (err) {
      console.error(err);
      setStatus('error');
      const errorMsg = err.response?.data?.detail || "Failed to connect to agent backend";
      setError(errorMsg);
      setMessages(prev => [...prev, { 
        type: 'agent', 
        content: `Error: ${errorMsg}` 
      }]);
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="min-h-screen flex flex-col">
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-6 py-8">
        
        {/* Empty State - Centered Welcome */}
        {!hasMessages && (
          <div className="flex-1 flex flex-col items-center justify-center max-w-2xl mx-auto w-full animate-fade-in-up">
            
            {/* Decorative Orb */}
            <Orb/>
            
            {/* Greeting */}
            <div className="text-center mb-12">
              <h1 className="text-2xl text-purple-400 mb-2 font-light">
                Hi, I'm TaskFlow
              </h1>
              <p className="text-4xl font-bold text-slate-900">
                How can I assist you today?
              </p>
            </div>

            {/* Input Field */}
            <form onSubmit={handleSubmit} className="w-full mb-8">
              <div className="relative group">
                <input
                  type="text"
                  value={task}
                  onChange={(e) => setTask(e.target.value)}
                  placeholder="Ask me anything..."
                  className="w-full px-6 py-4 pr-14 text-base bg-white rounded-2xl shadow-lg border border-slate-200 focus:border-purple-400 focus:ring-4 focus:ring-purple-400/10 outline-none transition-all placeholder:text-slate-400"
                  disabled={status === 'planning' || status === 'executing' || status === 'verifying'}
                />
                <button
                  type="submit"
                  disabled={!task.trim() || (status !== 'idle' && status !== 'success' && status !== 'error')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-gradient-to-br from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl flex items-center justify-center transition-all shadow-md"
                >
                  {status === 'idle' || status === 'success' || status === 'error' ? (
                    <Forward className="w-5 h-5" />
                  ) : (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  )}
                </button>
              </div>
              {error && (
                <div className="mt-3 flex items-center justify-center gap-2 text-red-600 text-sm font-medium">
                  <AlertCircle className="w-4 h-4" />
                  {error}
                </div>
              )}
            </form>

            {/* Quick Actions */}
            <div className="w-full">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {quickActions.map((action, idx) => (
                  <QuickActionCard
                    key={idx}
                    icon={action.icon}
                    title={action.title}
                    description={action.description}
                    onClick={() => handleQuickAction(action)}
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Chat State - Messages at top, input at bottom */}
        {hasMessages && (
          <>
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto space-y-4 mb-6">
              {messages.map((msg, idx) => (
                <MessageBubble key={idx} type={msg.type} content={msg.content} />
              ))}
              
              {/* Status Badge */}
              {status !== 'idle' && status !== 'success' && (
                <div className="flex justify-center py-4">
                  <StatusBadge status={status} />
                </div>
              )}

              {/* Plan Section */}
              {plan && (
                <div className="animate-fade-in-up">
                  <div className="flex items-center gap-2 mb-4">
                     <BrainCircuit className="w-5 h-5 text-purple-500" />
                     <h2 className="text-lg font-semibold text-slate-800">Execution Plan</h2>
                  </div>
                  
                  <div className="glass-card rounded-2xl shadow-sm border border-slate-200 p-1 space-y-2">
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
                            isCompleted={true}
                            isCurrent={false}
                         />
                       ))}
                     </div>
                  </div>
                </div>
              )}

              {/* Results Section */}
              {result && (
                <div className="animate-fade-in-up">
                   <ResultViewer data={result.data} summary={result.summary} />
                </div>
              )}
            </div>

            {/* Fixed Input at Bottom */}
            <div className="sticky bottom-0 bg-gradient-to-t from-slate-50 via-purple-50/20 to-transparent pt-4 pb-2">
              <form onSubmit={handleSubmit}>
                <div className="relative group">
                  <input
                    type="text"
                    value={task}
                    onChange={(e) => setTask(e.target.value)}
                    placeholder="Ask me anything..."
                    className="w-full px-6 py-4 pr-14 text-base bg-white rounded-2xl shadow-lg border border-slate-200 focus:border-purple-400 focus:ring-4 focus:ring-purple-400/10 outline-none transition-all placeholder:text-slate-400"
                    disabled={status === 'planning' || status === 'executing' || status === 'verifying'}
                  />
                  <button
                    type="submit"
                    disabled={!task.trim() || (status !== 'idle' && status !== 'success' && status !== 'error')}
                    className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-gradient-to-br from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl flex items-center justify-center transition-all shadow-md"
                  >
                    {status === 'idle' || status === 'success' || status === 'error' ? (
                      <Send className="w-5 h-5" />
                    ) : (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    )}
                  </button>
                </div>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
