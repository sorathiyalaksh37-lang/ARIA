import React from 'react';
import { MoreVertical, Edit2, Trash2, Shield, User as UserIcon } from 'lucide-react';
import { User, UserRole } from '../../types';

interface UserTableProps {
  users: User[];
  onEdit: (user: User) => void;
  onDelete: (id: string) => void;
}

export const UserTable: React.FC<UserTableProps> = ({ users, onEdit, onDelete }) => {
  const getRoleBadge = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN: return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case UserRole.COORDINATOR: return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="bg-surface-900 border border-surface-800 rounded-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-surface-950 border-b border-surface-800 text-slate-400 text-sm">
              <th className="py-4 px-6 font-medium">User</th>
              <th className="py-4 px-6 font-medium">Role</th>
              <th className="py-4 px-6 font-medium">Status</th>
              <th className="py-4 px-6 font-medium">Last Login</th>
              <th className="py-4 px-6 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-800">
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-surface-800/50 transition-colors group">
                <td className="py-4 px-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-surface-800 flex items-center justify-center text-slate-400 border border-surface-700">
                      {user.avatar_url ? (
                        <img src={user.avatar_url} alt={user.full_name} className="w-full h-full rounded-full object-cover" />
                      ) : (
                        <UserIcon className="w-5 h-5" />
                      )}
                    </div>
                    <div>
                      <div className="text-white font-medium">{user.full_name}</div>
                      <div className="text-slate-500 text-sm">{user.email}</div>
                    </div>
                  </div>
                </td>
                <td className="py-4 px-6">
                  <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border flex w-fit items-center gap-1.5 ${getRoleBadge(user.role)}`}>
                    {user.role === UserRole.ADMIN && <Shield className="w-3 h-3" />}
                    {user.role.replace('_', ' ')}
                  </span>
                </td>
                <td className="py-4 px-6">
                  <span className="flex items-center gap-2 text-sm">
                    <div className={`w-2 h-2 rounded-full ${user.is_active ? 'bg-emerald-500' : 'bg-slate-600'}`} />
                    <span className={user.is_active ? 'text-slate-300' : 'text-slate-500'}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </span>
                </td>
                <td className="py-4 px-6 text-sm text-slate-400">
                  {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                </td>
                <td className="py-4 px-6 text-right">
                  <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button 
                      onClick={() => onEdit(user)}
                      className="p-2 text-slate-400 hover:text-white hover:bg-surface-700 rounded-lg transition-colors"
                      title="Edit"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button 
                      onClick={() => onDelete(user.id)}
                      className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            
            {users.length === 0 && (
              <tr>
                <td colSpan={5} className="py-8 text-center text-slate-500">
                  No users found matching your search.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      {/* Basic Pagination Mock */}
      <div className="bg-surface-950 border-t border-surface-800 p-4 flex items-center justify-between text-sm text-slate-400">
        <div>Showing 1 to {users.length} of {users.length} entries</div>
        <div className="flex gap-2">
          <button className="px-3 py-1 bg-surface-900 border border-surface-800 rounded hover:bg-surface-800 transition-colors disabled:opacity-50">Previous</button>
          <button className="px-3 py-1 bg-surface-900 border border-surface-800 rounded hover:bg-surface-800 transition-colors disabled:opacity-50">Next</button>
        </div>
      </div>
    </div>
  );
};
