// src/utils/helpers.ts
import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { IncidentSeverity, IncidentStatus, AmbulanceStatus } from '../types';

// ---- Date helpers ----------------------------------------

export const formatDate = (iso: string, pattern = 'dd MMM yyyy, HH:mm') =>
  format(parseISO(iso), pattern);

export const timeAgo = (iso: string) =>
  formatDistanceToNow(parseISO(iso), { addSuffix: true });

// ---- Severity / Status badge colours --------------------

export const SEVERITY_COLORS: Record<IncidentSeverity, string> = {
  [IncidentSeverity.CRITICAL]: 'text-red-400   bg-red-900/30   border-red-700',
  [IncidentSeverity.MODERATE]:   'text-yellow-400 bg-yellow-900/30 border-yellow-700',
  [IncidentSeverity.LOW]:      'text-green-400  bg-green-900/30  border-green-700',
};

export const SEVERITY_DOT: Record<IncidentSeverity, string> = {
  [IncidentSeverity.CRITICAL]: 'bg-red-500',
  [IncidentSeverity.MODERATE]:   'bg-yellow-500',
  [IncidentSeverity.LOW]:      'bg-green-500',
};

export const INCIDENT_STATUS_COLORS: Record<IncidentStatus, string> = {
  [IncidentStatus.PENDING]: 'text-gray-400  bg-gray-800',
  [IncidentStatus.PROCESSING]: 'text-amber-400 bg-amber-900/30',
  [IncidentStatus.AWAITING_APPROVAL]: 'text-orange-400 bg-orange-900/30',
  [IncidentStatus.APPROVED]: 'text-green-400 bg-green-900/30',
  [IncidentStatus.REJECTED]: 'text-red-400 bg-red-900/30',
  [IncidentStatus.DISPATCHED]: 'text-blue-400  bg-blue-900/30',
  [IncidentStatus.COMPLETED]: 'text-emerald-400 bg-emerald-900/30',
  [IncidentStatus.CANCELLED]: 'text-slate-400 bg-slate-800',
};

export const AMBULANCE_STATUS_COLORS: Record<AmbulanceStatus, string> = {
  [AmbulanceStatus.AVAILABLE]:    'text-green-400  bg-green-900/30',
  [AmbulanceStatus.EN_ROUTE]:     'text-blue-400   bg-blue-900/30',
  [AmbulanceStatus.ON_SCENE]:     'text-purple-400 bg-purple-900/30',
  [AmbulanceStatus.TRANSPORTING]: 'text-cyan-400   bg-cyan-900/30',
  [AmbulanceStatus.AT_HOSPITAL]:  'text-yellow-400 bg-yellow-900/30',
  [AmbulanceStatus.OFFLINE]:      'text-red-400    bg-red-900/30',
};

// ---- Misc ------------------------------------------------

/** Truncate long strings */
export const truncate = (str: string, maxLen = 60) =>
  str.length > maxLen ? `${str.slice(0, maxLen)}…` : str;

/** Calculate capacity percentage */
export const capacityPct = (used: number, total: number) =>
  total === 0 ? 0 : Math.round((used / total) * 100);

/** Format phone numbers */
export const formatPhone = (phone: string) =>
  phone.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');

/** Debounce utility */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

/** Clamp a number to [min, max] */
export const clamp = (n: number, min: number, max: number) =>
  Math.min(Math.max(n, min), max);
