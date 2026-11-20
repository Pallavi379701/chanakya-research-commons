import React, { useState } from 'react';
import { User, Shield, BookOpen, ExternalLink, Tag, Users, CheckCircle2, UserPlus, Edit3, Plus, X } from 'lucide-react';
import { api } from '../services/api';

export function ProfilePage({ currentUser, onSwitchUser, allUsers, onUserRegistered }) {
  const [selectedUserId, setSelectedUserId] = useState(currentUser?.id || 1);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);

  // New User Registration Form State
  const [newName, setNewName] = useState('');
  const [newUsername, setNewUsername] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newRole, setNewRole] = useState('student');
  const [newDept, setNewDept] = useState('Data Science & AI');
  const [newInterests, setNewInterests] = useState('');
  const [newTags, setNewTags] = useState('');
  const [newBio, setNewBio] = useState('');
  const [newPubUrl, setNewPubUrl] = useState('');
  const [submittingNew, setSubmittingNew] = useState(false);

  // Edit Profile Form State
  const [editName, setEditName] = useState(currentUser?.full_name || '');
  const [editRole, setEditRole] = useState(currentUser?.role || 'student');
  const [editDept, setEditDept] = useState(currentUser?.department || 'Computer Science');
  const [editInterests, setEditInterests] = useState(currentUser?.research_interests || '');
  const [editTags, setEditTags] = useState(currentUser?.interest_tags || '');
  const [editBio, setEditBio] = useState(currentUser?.bio || '');
  const [editPubUrl, setEditPubUrl] = useState(currentUser?.publication_url || '');
  const [submittingEdit, setSubmittingEdit] = useState(false);

  const handleSelect = (e) => {
    const uId = parseInt(e.target.value);
    setSelectedUserId(uId);
    const targetUser = allUsers.find(u => u.id === uId);
    if (targetUser && onSwitchUser) {
      onSwitchUser(targetUser);
      setEditName(targetUser.full_name);
      setEditRole(targetUser.role);
      setEditDept(targetUser.department);
      setEditInterests(targetUser.research_interests || '');
      setEditTags(targetUser.interest_tags || '');
      setEditBio(targetUser.bio || '');
      setEditPubUrl(targetUser.publication_url || '');
    }
  };

  const handleRegisterNewMember = async (e) => {
    e.preventDefault();
    if (!newName.trim()) return;
    setSubmittingNew(true);
    try {
      const generatedUsername = newUsername.trim() || newName.toLowerCase().replace(/[^a-z0-9]/g, '') + Math.floor(Math.random() * 100);
      const generatedEmail = newEmail.trim() || `${generatedUsername}@chanakya.edu.in`;
      
      const createdUser = await api.register({
        full_name: newName,
        username: generatedUsername,
        email: generatedEmail,
        password: "Password@123",
        role: newRole,
        department: newDept,
        research_interests: newInterests,
        interest_tags: newTags,
        bio: newBio,
        publication_url: newPubUrl
      });

      alert(`Successfully registered ${createdUser.full_name}! Now active.`);
      setShowAddModal(false);
      setNewName('');
      setNewUsername('');
      setNewEmail('');
      setNewInterests('');
      setNewTags('');
      setNewBio('');
      setNewPubUrl('');

      if (onSwitchUser) onSwitchUser(createdUser);
      if (onUserRegistered) onUserRegistered(createdUser);
    } catch (err) {
      alert("Registration error: " + (err.message || "Failed to register"));
    } finally {
      setSubmittingNew(false);
    }
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    if (!currentUser) return;
    setSubmittingEdit(true);
    try {
      const updated = await api.updateUser(currentUser.id, {
        full_name: editName,
        role: editRole,
        department: editDept,
        research_interests: editInterests,
        interest_tags: editTags,
        bio: editBio,
        publication_url: editPubUrl
      });
      alert("Profile updated successfully!");
      setShowEditModal(false);
      if (onSwitchUser) onSwitchUser(updated);
    } catch (err) {
      alert("Update error: " + (err.message || "Failed to update"));
    } finally {
      setSubmittingEdit(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header & Actions */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <User className="w-5 h-5 text-amber-500" /> Researcher Profile & Accounts
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Add real-world faculty, researchers, and students, or edit your current profile.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAddModal(true)}
            className="px-3.5 py-1.5 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold rounded-lg text-xs transition-all shadow-sm flex items-center gap-1.5"
          >
            <UserPlus className="w-3.5 h-3.5" /> Add Real Member
          </button>
          <button
            onClick={() => {
              setEditName(currentUser?.full_name || '');
              setEditRole(currentUser?.role || 'student');
              setEditDept(currentUser?.department || 'Computer Science');
              setEditInterests(currentUser?.research_interests || '');
              setEditTags(currentUser?.interest_tags || '');
              setEditBio(currentUser?.bio || '');
              setEditPubUrl(currentUser?.publication_url || '');
              setShowEditModal(true);
            }}
            className="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-lg text-xs transition-all flex items-center gap-1.5"
          >
            <Edit3 className="w-3.5 h-3.5" /> Edit Profile
          </button>
        </div>
      </div>

      {/* Account Selector */}
      <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 flex items-center justify-between text-xs">
        <span className="font-semibold text-slate-700">Switch Active Member / Role:</span>
        <select
          value={currentUser?.id || 1}
          onChange={handleSelect}
          className="text-xs font-bold px-3 py-1.5 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none"
        >
          {allUsers.map(u => (
            <option key={u.id} value={u.id}>
              {u.full_name} ({u.role.toUpperCase()}) - {u.department}
            </option>
          ))}
        </select>
      </div>

      {/* Active Profile Card */}
      {currentUser && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-5">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-2xl bg-slate-900 text-amber-400 font-extrabold text-2xl flex items-center justify-center shrink-0 shadow-md">
              {currentUser.full_name?.charAt(0)}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-slate-900">{currentUser.full_name}</h2>
                <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                  currentUser.role === 'admin'
                    ? 'bg-rose-100 text-rose-800'
                    : currentUser.role === 'faculty'
                    ? 'bg-purple-100 text-purple-800'
                    : currentUser.role === 'researcher'
                    ? 'bg-indigo-100 text-indigo-800'
                    : 'bg-emerald-100 text-emerald-800'
                }`}>
                  {currentUser.role}
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">{currentUser.email} • {currentUser.department}</p>
              <p className="text-xs text-slate-700 mt-2 italic leading-relaxed">"{currentUser.bio || "Member of Chanakya Research Commons."}"</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-slate-100">
            <div>
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Research Interests</span>
              <p className="text-xs text-slate-800 leading-relaxed font-medium">
                {currentUser.research_interests || "General Research & Development"}
              </p>
            </div>

            <div>
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Publications & Links</span>
              {currentUser.publication_url ? (
                <a
                  href={currentUser.publication_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-1.5"
                >
                  <ExternalLink className="w-3.5 h-3.5" /> View Scholarly Profile
                </a>
              ) : (
                <span className="text-xs text-slate-400">None linked</span>
              )}
            </div>
          </div>

          {/* Research Interest Tags */}
          {currentUser.interest_tags && (
            <div className="pt-2 border-t border-slate-100">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">Topic Tags</span>
              <div className="flex flex-wrap gap-1.5">
                {currentUser.interest_tags.split(",").map((t, idx) => (
                  <span key={idx} className="px-2.5 py-1 bg-slate-100 text-slate-700 font-medium text-xs rounded-lg flex items-center gap-1">
                    <Tag className="w-3 h-3 text-slate-400" /> #{t.trim()}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Follow Stats */}
          <div className="flex items-center gap-6 pt-3 border-t border-slate-100 text-xs">
            <div>
              <strong className="text-slate-900 text-sm font-bold">{currentUser.followers_count || 0}</strong> <span className="text-slate-500">Followers</span>
            </div>
            <div>
              <strong className="text-slate-900 text-sm font-bold">{currentUser.following_count || 0}</strong> <span className="text-slate-500">Following</span>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 1: ADD REAL MEMBER */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b pb-3">
              <h3 className="text-base font-bold text-slate-900">Add Real Member / Colleague</h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-xs text-slate-500">
              Register yourself, a classmate, or a professor with real-world names, department, and research topics.
            </p>

            <form onSubmit={handleRegisterNewMember} className="space-y-3">
              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase">Full Name *</label>
                <input
                  type="text"
                  required
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="e.g. Pallavi BN or Dr. Ramesh Rao"
                  className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-bold text-slate-700 uppercase">Role</label>
                  <select
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value)}
                    className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none"
                  >
                    <option value="student">Student</option>
                    <option value="faculty">Faculty</option>
                    <option value="researcher">Researcher</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
                <div>
                  <label className="text-[11px] font-bold text-slate-700 uppercase">Department</label>
                  <select
                    value={newDept}
                    onChange={(e) => setNewDept(e.target.value)}
                    className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none"
                  >
                    <option>Computer Science</option>
                    <option>Data Science & AI</option>
                    <option>Electrical Engineering</option>
                    <option>Biotechnology</option>
                    <option>Mathematics & Computing</option>
                    <option>School of Management</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase">Research Interests</label>
                <input
                  type="text"
                  value={newInterests}
                  onChange={(e) => setNewInterests(e.target.value)}
                  placeholder="e.g. Large Language Models, Graph Neural Networks, Data Warehousing"
                  className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase">Topic Tags (comma-separated)</label>
                <input
                  type="text"
                  value={newTags}
                  onChange={(e) => setNewTags(e.target.value)}
                  placeholder="e.g. AI, NLP, Transformers, Big Data"
                  className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase">Bio / Description</label>
                <textarea
                  rows="2"
                  value={newBio}
                  onChange={(e) => setNewBio(e.target.value)}
                  placeholder="Brief biography or lab affiliation..."
                  className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                ></textarea>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase">Google Scholar or Profile Link</label>
                <input
                  type="url"
                  value={newPubUrl}
                  onChange={(e) => setNewPubUrl(e.target.value)}
                  placeholder="https://scholar.google.com/citations?user=..."
                  className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingNew}
                  className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold rounded-lg text-xs"
                >
                  {submittingNew ? "Registering..." : "Add to Chanakya Commons"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: EDIT CURRENT PROFILE */}
      {showEditModal && (
        <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b pb-3">
              <h3 className="text-base font-bold text-slate-900">Edit Profile</h3>
              <button onClick={() => setShowEditModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpdateProfile} className="space-y-3">
              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase">Full Name *</label>
                <input
                  type="text"
                  required
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-bold text-slate-700 uppercase">Role</label>
                  <select
                    value={editRole}
                    onChange={(e) => setEditRole(e.target.value)}
                    className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none"
                  >
                    <option value="student">Student</option>
                    <option value="faculty">Faculty</option>
                    <option value="researcher">Researcher</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
                <div>
                  <label className="text-[11px] font-bold text-slate-700 uppercase">Department</label>
                  <select
                    value={editDept}
                    onChange={(e) => setEditDept(e.target.value)}
                    className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none"
                  >
                    <option>Computer Science</option>
                    <option>Data Science & AI</option>
                    <option>Electrical Engineering</option>
                    <option>Biotechnology</option>
                    <option>Mathematics & Computing</option>
                    <option>School of Management</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase">Research Interests</label>
                <input
                  type="text"
                  value={editInterests}
                  onChange={(e) => setEditInterests(e.target.value)}
                  className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase">Topic Tags</label>
                <input
                  type="text"
                  value={editTags}
                  onChange={(e) => setEditTags(e.target.value)}
                  className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase">Bio</label>
                <textarea
                  rows="2"
                  value={editBio}
                  onChange={(e) => setEditBio(e.target.value)}
                  className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                ></textarea>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase">Google Scholar Link</label>
                <input
                  type="url"
                  value={editPubUrl}
                  onChange={(e) => setEditPubUrl(e.target.value)}
                  className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingEdit}
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-lg text-xs"
                >
                  {submittingEdit ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
