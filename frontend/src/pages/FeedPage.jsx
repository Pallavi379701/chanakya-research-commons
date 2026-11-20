import React, { useState, useEffect } from 'react';
import { MessageSquare, ThumbsUp, Send, Paperclip, Tag, PlusCircle, Sparkles, Filter, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export function FeedPage({ currentUser }) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [feedMode, setFeedMode] = useState('personalized'); // 'personalized' or 'all'
  const [selectedTag, setSelectedTag] = useState('');
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');
  const [newTags, setNewTags] = useState('Machine Learning, Systems');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [expandedComments, setExpandedComments] = useState({});
  const [commentInputs, setCommentInputs] = useState({});

  const loadFeed = async () => {
    setLoading(true);
    try {
      if (feedMode === 'personalized') {
        const data = await api.getFeed(currentUser?.id || 1);
        setPosts(data);
      } else {
        const params = selectedTag ? `?tag=${encodeURIComponent(selectedTag)}` : '';
        const data = await api.getPosts(params);
        setPosts(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFeed();
  }, [feedMode, selectedTag, currentUser]);

  const handleCreatePost = async (e) => {
    e.preventDefault();
    if (!newTitle.trim() || !newContent.trim()) return;
    setIsSubmitting(true);
    try {
      await api.createPost({
        title: newTitle,
        content: newContent,
        tags: newTags
      }, currentUser?.id || 1);
      setNewTitle('');
      setNewContent('');
      loadFeed();
    } catch (err) {
      alert("Failed to create post");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpvote = async (postId) => {
    try {
      const res = await api.toggleUpvote(postId, currentUser?.id || 1);
      setPosts(prev => prev.map(p => {
        if (p.id === postId) {
          return {
            ...p,
            upvotes: res.upvotes,
            has_upvoted: res.action === 'upvoted'
          };
        }
        return p;
      }));
    } catch (err) {
      console.error(err);
    }
  };

  const toggleComments = async (postId) => {
    if (expandedComments[postId]) {
      setExpandedComments(prev => ({ ...prev, [postId]: null }));
    } else {
      try {
        const comments = await api.getComments(postId);
        setExpandedComments(prev => ({ ...prev, [postId]: comments }));
      } catch (err) {
        console.error(err);
      }
    }
  };

  const handleAddComment = async (postId) => {
    const text = commentInputs[postId];
    if (!text || !text.trim()) return;
    try {
      await api.addComment(postId, text, currentUser?.id || 1);
      setCommentInputs(prev => ({ ...prev, [postId]: '' }));
      const updatedComments = await api.getComments(postId);
      setExpandedComments(prev => ({ ...prev, [postId]: updatedComments }));
      setPosts(prev => prev.map(p => p.id === postId ? { ...p, comments_count: (p.comments_count || 0) + 1 } : p));
    } catch (err) {
      alert("Failed to submit reply");
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Feed Controls Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Campus Research Discussions</h1>
          <p className="text-xs text-slate-500 mt-0.5">Connect, critique methodologies, share preprints, and collaborate across departments.</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setFeedMode('personalized')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
              feedMode === 'personalized'
                ? 'bg-slate-900 text-amber-400 shadow-sm'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" /> For You (Personalized Feed)
          </button>
          <button
            onClick={() => { setFeedMode('all'); setSelectedTag(''); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              feedMode === 'all'
                ? 'bg-slate-900 text-white shadow-sm'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            All Campus Posts
          </button>
        </div>
      </div>

      {/* Post Creator Box */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-3">
        <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
          <PlusCircle className="w-4 h-4 text-amber-500" /> Start a Research Discussion
        </h3>
        <form onSubmit={handleCreatePost} className="space-y-3">
          <input
            type="text"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="Topic or Research Question (e.g., 'Convergence behavior of LoRA on low VRAM GPUs?')"
            className="w-full px-3.5 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 font-medium"
          />
          <textarea
            rows="3"
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
            placeholder="Provide context, methodology findings, questions for peers, or citations..."
            className="w-full px-3.5 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
          ></textarea>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
            <div className="flex items-center gap-2">
              <Tag className="w-3.5 h-3.5 text-slate-400" />
              <input
                type="text"
                value={newTags}
                onChange={(e) => setNewTags(e.target.value)}
                placeholder="Tags (e.g. LLMs, Optimization)"
                className="px-2 py-1 text-xs bg-slate-50 border border-slate-200 rounded text-slate-700 w-52 focus:outline-none"
              />
            </div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-semibold rounded-lg text-xs transition-all shadow-sm flex items-center justify-center gap-1.5"
            >
              <Send className="w-3.5 h-3.5" /> Post Discussion
            </button>
          </div>
        </form>
      </div>

      {/* Discussion List */}
      {loading ? (
        <div className="text-center py-12 text-slate-400 text-xs">Loading campus discussions...</div>
      ) : posts.length === 0 ? (
        <div className="bg-white p-8 rounded-xl border border-slate-200 text-center text-slate-500 text-xs">
          No discussion posts found in this feed. Start the conversation!
        </div>
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <div key={post.id} className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-3">
              {/* Author & Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-full bg-slate-800 text-amber-400 flex items-center justify-center text-xs font-bold">
                    {post.author?.full_name?.charAt(0) || "U"}
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-900">{post.author?.full_name || "Campus Member"}</h4>
                    <p className="text-[10px] text-slate-500">
                      {post.author?.role?.toUpperCase()} • {post.author?.department} • {new Date(post.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-1.5">
                  {post.tags && post.tags.split(',').slice(0, 2).map((t, idx) => (
                    <span key={idx} className="text-[10px] px-2 py-0.5 bg-slate-100 text-slate-600 font-medium rounded-full">
                      #{t.trim()}
                    </span>
                  ))}
                </div>
              </div>

              {/* Title & Body */}
              <h3 className="text-sm font-bold text-slate-900 leading-snug">{post.title}</h3>
              <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-line">{post.content}</p>

              {/* Attached Paper */}
              {post.attached_paper && (
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1">
                  <div className="flex items-center gap-1.5 text-indigo-600 font-semibold text-[11px]">
                    <Paperclip className="w-3.5 h-3.5" /> Attached Scholarly Paper
                  </div>
                  <div className="font-bold text-slate-800">{post.attached_paper.title}</div>
                  <div className="text-[10px] text-slate-500">{post.attached_paper.authors} ({post.attached_paper.year}) • {post.attached_paper.venue}</div>
                </div>
              )}

              {/* Action Buttons: Upvotes & Comments */}
              <div className="flex items-center gap-3 pt-2 border-t border-slate-100 text-xs">
                <button
                  onClick={() => handleUpvote(post.id)}
                  className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium transition-all ${
                    post.has_upvoted
                      ? 'bg-amber-100 text-amber-800 font-bold'
                      : 'bg-slate-50 hover:bg-slate-100 text-slate-600'
                  }`}
                >
                  <ThumbsUp className={`w-3.5 h-3.5 ${post.has_upvoted ? 'fill-amber-600 text-amber-600' : ''}`} />
                  <span>{post.upvotes} Upvotes</span>
                </button>

                <button
                  onClick={() => toggleComments(post.id)}
                  className="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 text-slate-600 rounded-lg flex items-center gap-1.5 font-medium transition-all"
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>{post.comments_count || 0} Replies</span>
                </button>
              </div>

              {/* Expandable Comments Section */}
              {expandedComments[post.id] && (
                <div className="pt-3 border-t border-slate-100 space-y-3 bg-slate-50/50 p-3 rounded-lg">
                  <div className="space-y-2">
                    {expandedComments[post.id].length === 0 ? (
                      <p className="text-[11px] text-slate-400 italic">No comments yet. Be the first to reply!</p>
                    ) : (
                      expandedComments[post.id].map(c => (
                        <div key={c.id} className="p-2.5 bg-white rounded-lg border border-slate-200 text-xs space-y-1">
                          <div className="flex items-center justify-between text-[10px] text-slate-500">
                            <span className="font-bold text-slate-800">{c.user?.full_name || "Member"}</span>
                            <span>{new Date(c.created_at).toLocaleDateString()}</span>
                          </div>
                          <p className="text-slate-700">{c.content}</p>
                        </div>
                      ))
                    )}
                  </div>

                  {/* Reply Input */}
                  <div className="flex gap-2 pt-1">
                    <input
                      type="text"
                      value={commentInputs[post.id] || ''}
                      onChange={(e) => setCommentInputs({ ...commentInputs, [post.id]: e.target.value })}
                      placeholder="Write an academic reply..."
                      className="flex-1 px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-amber-500"
                    />
                    <button
                      onClick={() => handleAddComment(post.id)}
                      className="px-3 py-1.5 bg-slate-900 text-white rounded-lg text-xs font-semibold hover:bg-slate-800"
                    >
                      Reply
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
