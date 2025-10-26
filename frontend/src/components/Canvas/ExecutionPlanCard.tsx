import type { CampaignAsset } from '@/types';
import { Card } from '@/components/ui/card';
import { CheckCircle2, Circle, ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';

interface ExecutionPlanCardProps {
  asset: CampaignAsset | null;
}

export function ExecutionPlanCard({ asset }: ExecutionPlanCardProps) {
  const [expandedPhase, setExpandedPhase] = useState<number | null>(0);
  const [tab, setTab] = useState<'phases'|'checklist'|'milestones'|'metrics'|'recommendations'>('phases');
  const [showAllChecklist, setShowAllChecklist] = useState(false);

  if (!asset) {
    return <Card className="p-4"><p className="text-sm text-gray-500 text-center">No execution plan yet</p></Card>;
  }

  // Normalize plan shape so UI accepts different agent outputs
  const rawPlan = asset.content || {};

  const normalizePlan = (p: any) => {
    const plan: any = { ...p };

    // Normalize phases: accept either phases[] or pre_launch/launch/post_launch object shape
    if (!Array.isArray(plan.phases)) {
      const phases: any[] = [];
      const pre = plan.pre_launch || plan.preLaunch || plan.preLaunchPhase || plan.preLaunchPhase;
      const ln = plan.launch || plan.Launch || plan.launchPhase;
      const post = plan.post_launch || plan.postLaunch || plan.postLaunchPhase;

      if (pre) {
        phases.push({
          name: pre.name || 'Pre-Launch',
          duration: pre.duration || pre.days || pre.length || '',
          steps: pre.steps || pre.tasks || (Array.isArray(pre) ? pre : [])
        });
      }
      if (ln) {
        phases.push({
          name: ln.name || 'Launch',
          duration: ln.duration || ln.days || ln.length || '',
          steps: ln.steps || ln.tasks || (Array.isArray(ln) ? ln : [])
        });
      }
      if (post) {
        phases.push({
          name: post.name || 'Post-Launch',
          duration: post.duration || post.days || post.length || '',
          steps: post.steps || post.tasks || (Array.isArray(post) ? post : [])
        });
      }

      // fallback: if plan has a "phases" like object keys or "timeline" array
      if (phases.length === 0) {
        if (Array.isArray(plan.timeline)) {
          plan.phases = plan.timeline.map((t: any, i: number) => ({
            name: t.name || `Phase ${i+1}`,
            duration: t.duration || t.days || '',
            steps: t.tasks || t.steps || (Array.isArray(t) ? t : [])
          }));
        } else {
          const detected = ['phase','pre_launch','launch','post_launch','preLaunch','postLaunch'].reduce((acc: any[], key) => {
            if (plan[key]) acc.push(plan[key]);
            return acc;
          }, []);
          if (detected.length > 0) {
            plan.phases = detected.map((x: any, i: number) => ({
              name: x.name || `Phase ${i+1}`,
              duration: x.duration || x.days || '',
              steps: x.steps || x.tasks || (Array.isArray(x) ? x : [])
            }));
          }
        }
      } else {
        plan.phases = phases;
      }
    }

    // Normalize checklist: accept checklist[] or tasks/items[]
    if (!Array.isArray(plan.checklist)) {
      if (Array.isArray(plan.tasks)) plan.checklist = plan.tasks;
      else if (Array.isArray(plan.items)) plan.checklist = plan.items;
      else plan.checklist = plan.checklist || [];
    }

    // Normalize milestones
    if (!Array.isArray(plan.key_milestones)) {
      if (Array.isArray(plan.milestones)) plan.key_milestones = plan.milestones;
      else plan.key_milestones = plan.key_milestones || plan.milestones || [];
    }

    // Normalize metrics
    if (!Array.isArray(plan.success_metrics)) {
      if (Array.isArray(plan.metrics)) plan.success_metrics = plan.metrics;
      else plan.success_metrics = plan.success_metrics || plan.metrics || [];
    }

    // Normalize recommendations
    if (!plan.recommendations) {
      plan.recommendations = plan.recommendations || plan.recommendation || plan.advice || null;
    }

    // Ensure structure defaults
    plan.phases = Array.isArray(plan.phases) ? plan.phases : [];
    plan.checklist = Array.isArray(plan.checklist) ? plan.checklist : [];
    plan.key_milestones = Array.isArray(plan.key_milestones) ? plan.key_milestones : [];
    plan.success_metrics = Array.isArray(plan.success_metrics) ? plan.success_metrics : [];

    // Normalize phase step naming (step may be object)
    plan.phases = plan.phases.map((ph: any) => {
      const steps = (ph.steps || ph.tasks || []).map((s: any) => {
        if (typeof s === 'string') return s;
        if (s && typeof s === 'object') return s.task || s.title || s.name || JSON.stringify(s);
        return String(s);
      });
      return {
        name: ph.name || ph.title || 'Phase',
        duration: ph.duration || ph.days || '',
        steps
      };
    });

    return plan;
  };

  const plan = normalizePlan(rawPlan);

  const tabs = [
    { key: 'phases', label: 'Phases' },
    { key: 'checklist', label: 'Checklist' },
    { key: 'milestones', label: 'Milestones' },
    { key: 'metrics', label: 'Metrics' },
    { key: 'recommendations', label: 'Recommendations' },
  ] as const;

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">Execution Plan</h3>
        <div className="flex gap-2">
          {tabs.map(t => (
            <button
              key={t.key}
              onClick={() => setTab(t.key as any)}
              className={`px-3 py-1 text-xs rounded ${tab === t.key ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-700'}`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Phases */}
      {tab === 'phases' && plan.phases && plan.phases.length > 0 && (
        <div className="space-y-3">
          {plan.phases.map((phase: any, idx: number) => (
            <div key={idx} className="border rounded-lg overflow-hidden">
              <button
                onClick={() => setExpandedPhase(expandedPhase === idx ? null : idx)}
                className="w-full p-3 flex items-center justify-between hover:bg-gray-50 transition-colors text-left"
              >
                <div className="flex items-center gap-2 flex-1">
                  {expandedPhase === idx ? <ChevronDown className="w-4 h-4 text-gray-500" /> : <ChevronRight className="w-4 h-4 text-gray-500" />}
                  <span className="font-medium text-sm text-gray-900">{phase.name}</span>
                </div>
                <span className="text-xs text-gray-500 ml-2">{phase.duration}</span>
              </button>

              {expandedPhase === idx && phase.steps && (
                <div className="p-3 bg-gray-50 border-t">
                  <ul className="space-y-2">
                    {phase.steps.map((step: string, stepIdx: number) => (
                      <li key={stepIdx} className="flex items-start gap-2 text-sm text-gray-700">
                        <Circle className="w-3 h-3 mt-0.5 text-gray-400 flex-shrink-0" />
                        <span>{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Checklist */}
      {tab === 'checklist' && plan.checklist && plan.checklist.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium text-gray-700">Key Tasks ({plan.checklist.length})</h4>
            <button
              className="text-xs text-purple-600 underline"
              onClick={() => setShowAllChecklist((s) => !s)}
            >
              {showAllChecklist ? 'Show less' : 'Show all'}
            </button>
          </div>

          {showAllChecklist ? (
            <div className="max-h-80 overflow-y-auto space-y-2 p-2 bg-gray-50 rounded">
              {plan.checklist.map((item: any, i: number) => (
                <div key={i} className="flex items-start gap-2 p-2 rounded hover:bg-white">
                  {item.completed ? <CheckCircle2 className="w-4 h-4 mt-0.5 text-green-500" /> : <Circle className="w-4 h-4 mt-0.5 text-gray-300" />}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-700">{item.task || item}</p>
                    {item.priority && <span className="text-xs text-gray-500">{item.priority}</span>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {plan.checklist.slice(0, 6).map((item: any, i: number) => (
                <div key={i} className="flex items-start gap-2 p-2 rounded hover:bg-gray-50">
                  {item.completed ? <CheckCircle2 className="w-4 h-4 mt-0.5 text-green-500" /> : <Circle className="w-4 h-4 mt-0.5 text-gray-300" />}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-700">{item.task || item}</p>
                    {item.priority && <span className="text-xs text-gray-500">{item.priority}</span>}
                  </div>
                </div>
              ))}
              {plan.checklist.length > 6 && (
                <div className="text-xs text-gray-500">+{plan.checklist.length - 6} more tasks — click "Show all" to view</div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Milestones */}
      {tab === 'milestones' && plan.key_milestones && plan.key_milestones.length > 0 && (
        <ul className="space-y-2">
          {plan.key_milestones.map((m: any, i: number) => {
            let text = '';
            if (typeof m === 'string') text = m;
            else if (m && typeof m === 'object') {
              const milestone = m.milestone ?? m.title ?? m.name ?? JSON.stringify(m);
              const date = m.date ?? m.due ?? null;
              text = date ? `${milestone} — ${date}` : milestone;
            } else {
              text = String(m);
            }
            return (
              <li key={i} className="text-sm text-gray-700">• {text}</li>
            );
          })}
        </ul>
      )}

      {/* Metrics */}
      {tab === 'metrics' && plan.success_metrics && plan.success_metrics.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {plan.success_metrics.map((m: any, i: number) => {
            let label = '';
            if (typeof m === 'string') label = m;
            else if (m && typeof m === 'object') {
              const metric = m.metric ?? m.name ?? JSON.stringify(m);
              const target = m.target ?? m.value ?? null;
              label = target ? `${metric}: ${target}` : metric;
            } else {
              label = String(m);
            }
            return (
              <span key={i} className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">{label}</span>
            );
          })}
        </div>
      )}

      {/* Recommendations */}
      {tab === 'recommendations' && plan.recommendations && (
        <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
          <p className="text-sm text-yellow-800">{plan.recommendations}</p>
        </div>
      )}
    </Card>
  );
}