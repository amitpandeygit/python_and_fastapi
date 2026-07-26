"use client";
// "use client" marks this a client component: it runs in the browser,
// which is what lets it hold state and respond to typing.

import { useEffect, useState } from "react";

// The shape the API returns. Keeping this in sync with the Pydantic
// model is what "the contract" means in practice.
type Application = {
  id: number;
  applicant_name: string;
  monthly_income: number;
  amount_requested: number;
  purpose: string;
  status: string;
};

// Next.js only exposes env vars to browser code when the name starts
// with NEXT_PUBLIC_. Docker Compose sets this in Part 6; the fallback
// covers running the page outside a container.
//
// This value is used by the BROWSER, so it must be the port PUBLISHED
// on your machine (API_PORT in .env), never the api's internal 8000.
const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

export default function Home() {
  const [apps, setApps] = useState<Application[]>([]);
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  // Fetch the list from the API and put it in state.
  async function load() {
    try {
      const response = await fetch(`${API}/applications`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setApps(await response.json());
      setError("");
    } catch (e) {
      // A failure here is usually the API being down, or CORS.
      setError("Could not reach the API. Is it running?");
    }
  }

  // Run load() once, after the first render. The empty array is the
  // dependency list: nothing to watch, so it never repeats.
  useEffect(() => {
    load();
  }, []);

  async function submit() {
    if (name.trim().length < 2) {
      setError("Name must be at least 2 characters.");
      return;
    }
    const response = await fetch(`${API}/applications`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        applicant_name: name,
        monthly_income: 50000,
        amount_requested: 200000,
        purpose: "working_capital",
      }),
    });
    if (response.status === 422) {
      // The API rejected it. A real UI would read response.json()
      // and show the specific field errors it names.
      setError("The API rejected that input (422).");
      return;
    }
    setName("");     // clear the box
    load();          // and re-read the list
  }

  return (
    <main>
      <h1>Loan applications</h1>

      <div style={ { display: "flex", gap: 8, margin: "16px 0" } }>
        <input
          value={name}
          placeholder="Applicant name"
          onChange={(e) => setName(e.target.value)}
        />
        <button onClick={submit}>Submit</button>
      </div>

      {error && <p style={ { color: "crimson" } }>{error}</p>}

      <ul>
        {apps.map((a) => (
          // key lets React track list items efficiently.
          <li key={a.id}>
            #{a.id} — {a.applicant_name} ({a.status})
          </li>
        ))}
      </ul>

      {apps.length === 0 && !error && <p>No applications yet.</p>}
    </main>
  );
}