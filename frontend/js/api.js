async function request(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(response.status === 404 ? "Δεν βρέθηκε." : `Σφάλμα διακομιστή (${response.status}).`);
  }
  return response.json();
}

export const api = {
  tracks: () => request("/tracks"),
  track: (id) => request(`/tracks/${encodeURIComponent(id)}`),
  modules: () => request("/modules"),
  quiz: (id) => request(`/quizzes/${encodeURIComponent(id)}`),
  lesson: (id) => request(`/lessons/${encodeURIComponent(id)}`),
  answer: (exerciseId, submission) =>
    request(`/exercises/${encodeURIComponent(exerciseId)}/answer`, {
      method: "POST",
      body: JSON.stringify(submission),
    }),
};
