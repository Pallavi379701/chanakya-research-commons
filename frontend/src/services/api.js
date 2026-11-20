const API_BASE = import.meta.env.VITE_API_BASE || (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" ? "http://127.0.0.1:8000" : "");

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP Error ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

export const api = {
  // F1 Auth & Users
  login: (username, password) => request("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),
  register: (userData) => request("/auth/register", { method: "POST", body: JSON.stringify(userData) }),
  updateUser: (userId, userData) => request(`/auth/users/${userId}`, { method: "PUT", body: JSON.stringify(userData) }),
  getUsers: (params = "") => request(`/auth/users${params}`),
  getUser: (id) => request(`/auth/users/${id}`),
  followUser: (targetId, currentUserId) => request(`/auth/follow/${targetId}?current_user_id=${currentUserId}`, { method: "POST" }),
  followTopic: (topic, currentUserId) => request(`/auth/follow-topic?topic=${encodeURIComponent(topic)}&current_user_id=${currentUserId}`, { method: "POST" }),

  // F2 Posts & Feed
  getPosts: (params = "") => request(`/posts${params}`),
  getFeed: (currentUserId) => request(`/posts/feed?current_user_id=${currentUserId}`),
  createPost: (postData, currentUserId) => request(`/posts?current_user_id=${currentUserId}`, { method: "POST", body: JSON.stringify(postData) }),
  toggleUpvote: (postId, currentUserId) => request(`/posts/${postId}/upvote?current_user_id=${currentUserId}`, { method: "POST" }),
  getComments: (postId) => request(`/posts/${postId}/comments`),
  addComment: (postId, content, currentUserId, parentId = null) => 
    request(`/posts/${postId}/comments?current_user_id=${currentUserId}`, {
      method: "POST",
      body: JSON.stringify({ content, parent_comment_id: parentId })
    }),

  // F3 Library
  getMyLibrary: (currentUserId, collection = "") => request(`/library/my-items?current_user_id=${currentUserId}${collection ? `&collection_name=${encodeURIComponent(collection)}` : ""}`),
  getCollections: (currentUserId) => request(`/library/collections?current_user_id=${currentUserId}`),
  getCatalog: (params = "") => request(`/library/chanakya-catalog${params}`),
  savePaper: (paperId, notes, collectionName, currentUserId) => 
    request(`/library/save?current_user_id=${currentUserId}`, {
      method: "POST",
      body: JSON.stringify({ paper_id: paperId, notes, collection_name: collectionName })
    }),
  addManualPaper: (paperData, currentUserId) => 
    request(`/library/add-manual?current_user_id=${currentUserId}`, {
      method: "POST",
      body: JSON.stringify(paperData)
    }),

  // F4 Ingestion
  getIngestionStatus: () => request("/ingestion/status"),
  triggerRefresh: () => request("/ingestion/trigger-batch-refresh", { method: "POST" }),

  // F5 Unified Search
  search: (query, mode = "hybrid", currentUserId = 1) => 
    request(`/search?q=${encodeURIComponent(query)}&mode=${mode}&current_user_id=${currentUserId}`),

  // F6 Recommendations
  getRecommendedPapers: (currentUserId) => request(`/recommendations/papers?current_user_id=${currentUserId}`),
  getRecommendedMembers: (currentUserId) => request(`/recommendations/members?current_user_id=${currentUserId}`),
  getAlsoSaved: (paperId) => request(`/recommendations/also-saved/${paperId}`),

  // F7 Trends & Spam
  getTrendsSummary: () => request("/trends/summary"),
  getSpamFlags: () => request("/trends/spam-flags"),

  // F8 Assistant RAG
  askAssistant: (question) => request("/assistant/ask", { method: "POST", body: JSON.stringify({ question }) }),

  // F9 Analytics
  getDepartmentTrends: () => request("/analytics/department-trends"),
  getCollaborationNetwork: () => request("/analytics/collaboration-network"),
  getTopEngagedPapers: () => request("/analytics/top-engaged-papers"),
  getDrilldown: (department = null, topic = null) => {
    let url = "/analytics/drilldown";
    const q = [];
    if (department) q.push(`department=${encodeURIComponent(department)}`);
    if (topic) q.push(`topic=${encodeURIComponent(topic)}`);
    if (q.length > 0) url += `?${q.join("&")}`;
    return request(url);
  },

  // Evaluation
  runEvaluation: () => request("/evaluation/run")
};
