// Intents/ShowActionableSetupsIntent.swift
// Echo Copilot — App Intent: open the Radar tab filtered to Actionable setups
// Requires: AppIntents framework + Info.plist NSUserActivityTypes entry

import AppIntents

struct ShowActionableSetupsIntent: AppIntent {
    static let title: LocalizedStringResource = "Show Actionable Setups"
    static let description = IntentDescription("Opens Echo Copilot and shows only actionable trading setups on the Radar.")

    static let openAppWhenRun: Bool = true

    func perform() async throws -> some IntentResult {
        // The app will open to the Radar tab.
        // Deep-link to filter=actionable can be implemented via a shared UserDefaults
        // key or NotificationCenter post that RadarViewModel observes.
        UserDefaults.standard.set("actionable", forKey: "echo_pending_filter")
        return .result()
    }
}
