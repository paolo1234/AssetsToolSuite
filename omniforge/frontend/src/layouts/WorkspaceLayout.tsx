/**
 * OmniForge — WorkspaceLayout
 * Rigid CSS Grid layout (Principio 3): sidebar | canvas | inspector
 * No floating elements allowed outside modals.
 */

import React from 'react';

interface WorkspaceLayoutProps {
  sidebar: React.ReactNode;
  canvas: React.ReactNode;
  inspector: React.ReactNode;
  sidebarCollapsed?: boolean;
}

export default function WorkspaceLayout({
  sidebar,
  canvas,
  inspector,
  sidebarCollapsed = false,
}: WorkspaceLayoutProps) {
  return (
    <div
      className="w-full h-full grid transition-all duration-200"
      style={{
        gridTemplateColumns: sidebarCollapsed ? '48px 1fr 300px' : '250px 1fr 300px',
        gridTemplateRows: '1fr',
      }}
    >
      {/* Sidebar — fixed width region */}
      <aside className="bg-of-bg-800 border-r border-of-border overflow-y-auto overflow-x-hidden">
        {sidebar}
      </aside>

      {/* Canvas — flexible center region */}
      <main className="bg-of-bg-900 overflow-hidden relative">
        {canvas}
      </main>

      {/* Inspector — fixed width region */}
      <aside className="bg-of-bg-800 border-l border-of-border overflow-y-auto">
        {inspector}
      </aside>
    </div>
  );
}
