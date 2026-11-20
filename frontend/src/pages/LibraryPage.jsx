import React, { useState, useEffect } from 'react';
import { BookOpen, Folder, Bookmark, Plus, ExternalLink, StickyNote, Sparkles, Filter, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export function LibraryPage({ currentUser }) {
  const [viewMode, setViewMode] = useState('personal'); // 'personal' or 'catalog'
  const [myItems, setMyItems] = useState([]);
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState('');
  const [catalogItems, setCatalogItems] = useState([]);
  const [loading, setLoading] = useState(true);

  // Manual paper addition modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [manualTitle, setManualTitle] = useState('');
  const [manualAbstract, setManualAbstract] = useState('');
  const [manualAuthors, setManualAuthors] = useState('');
  const [manualDoi, setManualDoi] = useState('');
  const [manualArxiv, setManualArxiv] = useState('');
  const [manualDept, setManualDept] = useState('Computer Science');
  const [submittingManual, setSubmittingManual] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      if (viewMode === 'personal') {
        const [items, colls] = await Promise.all([
          api.getMyLibrary(currentUser?.id || 1, selectedCollection),
          api.getCollections(currentUser?.id || 1)
        ]);
        setMyItems(items);
        setCollections(colls);
      } else {
        const catalog = await api.getCatalog('?sort_by=saves');
        setCatalogItems(catalog);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [viewMode, selectedCollection, currentUser]);

  const handleAddManual = async (e) => {
    e.preventDefault();
    if (!manualTitle.trim()) return;
    setSubmittingManual(true);
    try {
      await api.addManualPaper({
        title: manualTitle,
        abstract: manualAbstract,
        authors: manualAuthors,
        doi: manualDoi,
        arxiv_id: manualArxiv,
        department: manualDept,
        source: manualArxiv ? "arXiv" : manualDoi ? "DOI" : "Manual",
        venue: "Academic Upload",
        year: 2026
      }, currentUser?.id || 1);
      setShowAddModal(false);
      setManualTitle('');
      setManualAbstract('');
      setManualAuthors('');
      setManualDoi('');
      setManualArxiv('');
      loadData();
    } catch (err) {
      alert("Failed to add paper");
    } finally {
      setSubmittingManual(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Mode Switcher */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-amber-500" /> Research Library & Collections
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Manage your personal bibliographies, private research annotations, and view the university-wide repository.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => { setViewMode('personal'); setSelectedCollection(''); }}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === 'personal'
                ? 'bg-slate-900 text-amber-400 shadow-sm'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            My Personal Collections
          </button>
          <button
            onClick={() => setViewMode('catalog')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === 'catalog'
                ? 'bg-slate-900 text-white shadow-sm'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            University-Wide Library Catalog
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-3.5 py-1.5 bg-amber-500 hover:bg-amber-600 text-slate-950 font-semibold rounded-lg text-xs transition-all shadow-sm flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" /> Add via DOI / arXiv
          </button>
        </div>
      </div>

      {/* PERSONAL COLLECTIONS VIEW */}
      {viewMode === 'personal' && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Left Column: Folders */}
          <div className="md:col-span-1 space-y-3">
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                <Folder className="w-4 h-4 text-amber-500" /> Personal Folders
              </h3>
              <div className="space-y-1 pt-1">
                <button
                  onClick={() => setSelectedCollection('')}
                  className={`w-full text-left px-3 py-2 rounded-lg text-xs font-medium flex items-center justify-between transition-all ${
                    selectedCollection === ''
                      ? 'bg-amber-50 text-amber-900 font-bold border border-amber-200'
                      : 'hover:bg-slate-50 text-slate-600'
                  }`}
                >
                  <span>All Saved Papers</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-semibold">
                    {myItems.length}
                  </span>
                </button>
                {collections.map(c => (
                  <button
                    key={c.collection_name}
                    onClick={() => setSelectedCollection(c.collection_name)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-xs font-medium flex items-center justify-between transition-all ${
                      selectedCollection === c.collection_name
                        ? 'bg-amber-50 text-amber-900 font-bold border border-amber-200'
                        : 'hover:bg-slate-50 text-slate-600'
                    }`}
                  >
                    <span>{c.collection_name}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-semibold">
                      {c.count}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Saved Items List */}
          <div className="md:col-span-3 space-y-4">
            {loading ? (
              <div className="text-center py-12 text-slate-400 text-xs">Loading personal library...</div>
            ) : myItems.length === 0 ? (
              <div className="bg-white p-8 rounded-xl border border-slate-200 text-center text-slate-500 text-xs">
                No papers saved in this collection yet. Search and click "Save to Library"!
              </div>
            ) : (
              myItems.map(item => (
                <div key={item.id} className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2.5">
                  <div className="flex items-start justify-between gap-3">
                    <h4 className="text-sm font-bold text-slate-900 leading-snug">{item.paper?.title}</h4>
                    <span className="shrink-0 px-2.5 py-0.5 bg-amber-100 text-amber-900 text-[10px] font-semibold rounded-full flex items-center gap-1">
                      <Bookmark className="w-3 h-3" /> Saved by {item.paper?.save_count || 1} at Chanakya
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 line-clamp-2">{item.paper?.abstract}</p>

                  {/* Private Note Badge */}
                  {item.notes && (
                    <div className="p-2.5 bg-amber-50/60 border border-amber-100 rounded-lg text-xs text-amber-900 flex items-start gap-2">
                      <StickyNote className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-bold text-[10px] uppercase text-amber-800 tracking-wider">Private Note: </span>
                        <span>{item.notes}</span>
                      </div>
                    </div>
                  )}

                  <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-500 pt-1 border-t border-slate-100">
                    <span className="font-medium text-slate-700">{item.paper?.authors}</span>
                    <span>•</span>
                    <span>{item.paper?.venue} ({item.paper?.year})</span>
                    <span>•</span>
                    <span className="bg-slate-100 px-2 py-0.5 rounded text-slate-700 font-medium">Folder: {item.collection_name}</span>
                    {item.paper?.doi && (
                      <span className="text-indigo-600 font-mono">DOI: {item.paper.doi}</span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* UNIVERSITY-WIDE CATALOG VIEW */}
      {viewMode === 'catalog' && (
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900">University-Wide Shared Repository</h3>
              <p className="text-xs text-slate-500">Every saved paper across all departments with aggregated campus save counts</p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 bg-amber-100 text-amber-800 rounded-full">
              {catalogItems.length} Papers Saved University-Wide
            </span>
          </div>

          <div className="space-y-3">
            {catalogItems.map(p => (
              <div key={p.id} className="p-4 rounded-xl border border-slate-100 hover:border-slate-300 transition-all space-y-2">
                <div className="flex items-start justify-between gap-3">
                  <h4 className="text-xs font-bold text-slate-900 leading-snug">{p.title}</h4>
                  <span className="shrink-0 px-2.5 py-0.5 bg-amber-100 text-amber-900 text-xs font-bold rounded-full">
                    ★ {p.save_count} Members Saved
                  </span>
                </div>
                <p className="text-xs text-slate-600 line-clamp-2">{p.abstract}</p>
                <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-500 pt-1">
                  <span>{p.authors}</span>
                  <span>•</span>
                  <span className="font-medium text-slate-700">{p.department}</span>
                  <span>•</span>
                  <span>{p.venue} ({p.year})</span>
                  <span className="ml-auto text-indigo-600 font-semibold bg-indigo-50 px-2 py-0.5 rounded">
                    {p.citation_count} Citations
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Manual Paper Import Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-slate-900">Add Paper via DOI, arXiv, or URL</h3>
            <p className="text-xs text-slate-500">
              Directly ingest a publication into your collection and the university-wide repository.
            </p>
            <form onSubmit={handleAddManual} className="space-y-3">
              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase">Paper Title *</label>
                <input
                  type="text"
                  required
                  value={manualTitle}
                  onChange={(e) => setManualTitle(e.target.value)}
                  placeholder="e.g. Scalable Graph Transformers for Heterogeneous Graphs"
                  className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-bold text-slate-700 uppercase">DOI</label>
                  <input
                    type="text"
                    value={manualDoi}
                    onChange={(e) => setManualDoi(e.target.value)}
                    placeholder="10.1145/3447548.3467200"
                    className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-bold text-slate-700 uppercase">arXiv ID</label>
                  <input
                    type="text"
                    value={manualArxiv}
                    onChange={(e) => setManualArxiv(e.target.value)}
                    placeholder="2305.12345"
                    className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase">Authors</label>
                <input
                  type="text"
                  value={manualAuthors}
                  onChange={(e) => setManualAuthors(e.target.value)}
                  placeholder="e.g. Alice Smith, Bob Johnson"
                  className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase">Department</label>
                <select
                  value={manualDept}
                  onChange={(e) => setManualDept(e.target.value)}
                  className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                >
                  <option>Computer Science</option>
                  <option>Data Science & AI</option>
                  <option>Electrical Engineering</option>
                  <option>Biotechnology</option>
                  <option>Mathematics & Computing</option>
                  <option>School of Management</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase">Abstract</label>
                <textarea
                  rows="3"
                  value={manualAbstract}
                  onChange={(e) => setManualAbstract(e.target.value)}
                  placeholder="Summary of research contribution..."
                  className="w-full mt-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                ></textarea>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingManual}
                  className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-semibold rounded-lg text-xs"
                >
                  {submittingManual ? "Ingesting..." : "Save to Repository"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
