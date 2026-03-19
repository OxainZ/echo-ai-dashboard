// Views/ContentView.swift
// Echo Copilot — Root tab container

import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var env: AppEnvironment

    var body: some View {
        TabView {
            RadarView()
                .tabItem {
                    Label("Radar", systemImage: "antenna.radiowaves.left.and.right")
                }

            OrdersView()
                .tabItem {
                    Label("Orders", systemImage: "cart.badge.plus")
                }

            JournalListView()
                .tabItem {
                    Label("Journal", systemImage: "book.closed")
                }

            AnalyticsView()
                .tabItem {
                    Label("Analytics", systemImage: "chart.line.uptrend.xyaxis")
                }

            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "gearshape")
                }
        }
        .tint(.accentColor)
    }
}

#Preview {
    ContentView()
        .environmentObject(AppEnvironment.preview)
        .preferredColorScheme(.dark)
}
