import React from "react";
import { ChevronRight } from "lucide-react";

export function LocalHeader({ breadcrumbs = [] }) {
  return (
    <>
      {/* Global GOLD gradient bar at the very top - indicates LOCAL DEV UI */}
      <div className="h-1.5 bg-gradient-to-r from-yellow-400 via-yellow-500 to-amber-500" />
      <header className="bg-white px-6 py-3 flex items-center border-b border-[var(--color-warm-gray-100)] z-1">
        {/* Breadcrumbs */}
        <div className="flex-1 flex items-center mr-6">
          {breadcrumbs.length > 0 && (
            <div className="flex items-center gap-2 text-sm transition-opacity duration-200 mr-4">
              {breadcrumbs.map((breadcrumb, index) => (
                <div key={index} className="flex items-center gap-2">
                  {index > 0 && <ChevronRight className="w-3 h-3 text-[var(--color-warm-gray-400)]" />}
                  {breadcrumb.href || breadcrumb.onClick ? (
                    <button
                      onClick={(e) => {
                        if (breadcrumb.onClick) {
                          e.preventDefault();
                          breadcrumb.onClick();
                        } else if (breadcrumb.href) {
                          // Handle navigation if needed
                        }
                      }}
                      className="text-[var(--color-warm-gray-600)] hover:text-[var(--color-warm-gray-900)] font-medium cursor-pointer transition-colors duration-200 text-sm"
                      style={{ fontSize: '0.875rem', fontWeight: '500' }}
                    >
                      {breadcrumb.label}
                    </button>
                  ) : (
                    <span
                      className="text-[var(--color-warm-gray-900)] font-medium cursor-default text-sm"
                      style={{ fontSize: '0.875rem', fontWeight: '500' }}
                    >
                      {breadcrumb.label}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* User section - simplified for local development */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-[var(--color-warm-gray-600)] font-medium">
            Local Development
          </span>
        </div>
      </header>
    </>
  );
}