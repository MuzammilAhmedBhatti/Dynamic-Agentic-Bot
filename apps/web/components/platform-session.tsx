"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

import { apiRequest } from "@/lib/api-client";

interface PlatformSessionProps {
  onConnected: (organizationId: string) => void;
}

export function PlatformSession({ onConnected }: PlatformSessionProps) {
  const [organizationId, setOrganizationId] = useState("");
  const [userId, setUserId] = useState("");
  const [status, setStatus] = useState("Enter the provisioned organization and local test user IDs.");
  const onConnectedRef = useRef(onConnected);

  useEffect(() => {
    onConnectedRef.current = onConnected;
  }, [onConnected]);

  useEffect(() => {
    const storedOrganization = window.localStorage.getItem("dynamic_agentic_org") ?? "";
    const storedUser = window.localStorage.getItem("dynamic_agentic_user") ?? "";
    if (!storedOrganization || !storedUser) return;
    queueMicrotask(() => {
      setOrganizationId(storedOrganization);
      setUserId(storedUser);
      setStatus("Restoring the previous local session…");
      void apiRequest("/api/v1/auth/test-session", {
        method: "POST",
        body: JSON.stringify({ user_id: storedUser }),
      })
        .then(() => {
          setStatus("Previous authenticated test session restored.");
          onConnectedRef.current(storedOrganization);
        })
        .catch((error: unknown) => {
          setStatus(error instanceof Error ? error.message : "Previous session could not be restored.");
        });
    });
  }, []);

  async function connect(event: FormEvent) {
    event.preventDefault();
    setStatus("Connecting…");
    try {
      await apiRequest("/api/v1/auth/test-session", {
        method: "POST",
        body: JSON.stringify({ user_id: userId }),
      });
      window.localStorage.setItem("dynamic_agentic_org", organizationId);
      window.localStorage.setItem("dynamic_agentic_user", userId);
      setStatus("Authenticated test session connected.");
      onConnected(organizationId);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Session connection failed.");
    }
  }

  return (
    <form className="panel grid gap-3 md:grid-cols-[1fr_1fr_auto]" onSubmit={connect}>
      <label className="field-label">
        Organization ID
        <input required value={organizationId} onChange={(event) => setOrganizationId(event.target.value)} />
      </label>
      <label className="field-label">
        Local test user ID
        <input required value={userId} onChange={(event) => setUserId(event.target.value)} />
      </label>
      <button className="primary-button self-end" type="submit">Connect</button>
      <p className="text-sm text-[var(--muted)] md:col-span-3" aria-live="polite">{status}</p>
    </form>
  );
}
