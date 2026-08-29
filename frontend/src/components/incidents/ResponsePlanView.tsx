import React from 'react';
import { ResponsePlan } from '../../types';
import { Bot, CheckCircle2, Circle, ArrowRight, Ambulance, Building2 } from 'lucide-react';

interface ResponsePlanViewProps {
  plan?: ResponsePlan;
  onApprove?: () => void;
  onReject?: () => void;
  onModify?: () => void;
}

export const ResponsePlanView: React.FC<ResponsePlanViewProps> = ({ 
  plan, 
  onApprove, 
  onReject, 
  onModify 
}) => {
  if (!plan) {
    return (
      <div className="bg-surface-900 border border-surface-800 rounded-xl p-8 text-center flex flex-col items-center">
        <Bot className="w-12 h-12 text-slate-600 mb-4" />
        <h3 className="text-white font-medium text-lg mb-2">No Active Response Plan</h3>
        <p className="text-slate-400">The ARIA AI is currently analyzing this incident to generate an optimal response strategy.</p>
        
        <div className="mt-6 flex space-x-2">
          <div className="w-2 h-2 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="w-2 h-2 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-900 border border-surface-800 rounded-xl p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center">
          <Bot className="w-5 h-5 text-primary-400" />
        </div>
        <div>
          <h3 className="text-white font-semibold text-lg flex items-center gap-2">
            AI Response Plan
            <span className="px-2 py-0.5 text-xs rounded-full bg-primary-500/20 text-primary-300 font-medium border border-primary-500/30">
              {plan.status}
            </span>
          </h3>
          <p className="text-slate-400 text-sm">Generated: {new Date(plan.generated_at).toLocaleString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Resource Allocation */}
        <div className="bg-surface-950 rounded-lg p-4 border border-surface-800">
          <h4 className="text-slate-300 font-medium mb-4 flex items-center gap-2">
            <ArrowRight className="w-4 h-4 text-primary-400" />
            Recommended Resources
          </h4>
          
          <div className="space-y-4">
            <div>
              <div className="flex items-center gap-2 text-sm text-slate-400 mb-2">
                <Ambulance className="w-4 h-4" /> Ambulances ({plan.recommended_ambulances.length})
              </div>
              <div className="flex flex-wrap gap-2">
                {plan.recommended_ambulances.map((ambId) => (
                  <span key={ambId} className="px-3 py-1 bg-surface-800 rounded-md text-sm text-slate-300 font-mono">
                    {ambId}
                  </span>
                ))}
              </div>
            </div>
            
            <div>
              <div className="flex items-center gap-2 text-sm text-slate-400 mb-2">
                <Building2 className="w-4 h-4" /> Hospitals ({plan.recommended_hospitals.length})
              </div>
              <div className="flex flex-wrap gap-2">
                {plan.recommended_hospitals.map((hospId) => (
                  <span key={hospId} className="px-3 py-1 bg-surface-800 rounded-md text-sm text-slate-300 font-mono">
                    {hospId}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-surface-950 rounded-lg p-4 border border-surface-800">
          <h4 className="text-slate-300 font-medium mb-4 flex items-center gap-2">
            <ArrowRight className="w-4 h-4 text-primary-400" />
            Execution Steps
          </h4>
          <ul className="space-y-3">
            {plan.instructions.map((step, idx) => (
              <li key={idx} className="flex gap-3 text-sm">
                <div className="mt-0.5">
                  {plan.status === 'COMPLETED' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  ) : plan.status === 'EXECUTING' && idx === 0 ? (
                    <div className="w-4 h-4 rounded-full border-2 border-primary-500 border-t-transparent animate-spin" />
                  ) : (
                    <Circle className="w-4 h-4 text-slate-600" />
                  )}
                </div>
                <span className="text-slate-300">{step}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {plan.status === 'PENDING' && (
        <div className="flex gap-3 pt-4 border-t border-surface-800">
          <button 
            onClick={onApprove}
            className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            Approve & Execute Plan
          </button>
          <button 
            onClick={onModify}
            className="px-6 bg-surface-800 hover:bg-surface-700 text-white font-medium py-2.5 rounded-lg transition-colors border border-surface-700"
          >
            Modify
          </button>
          <button 
            onClick={onReject}
            className="px-6 bg-red-500/10 hover:bg-red-500/20 text-red-500 font-medium py-2.5 rounded-lg transition-colors border border-red-500/20"
          >
            Reject
          </button>
        </div>
      )}
    </div>
  );
};
