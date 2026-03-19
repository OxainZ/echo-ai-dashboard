// Intents/EchoCopilotShortcuts.swift
// Echo Copilot — AppShortcutsProvider: registers intents with Siri automatically.
// No user setup required — these appear in Spotlight, Siri, and the Shortcuts app.

import AppIntents

struct EchoCopilotShortcuts: AppShortcutsProvider {

    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: ShowActionableSetupsIntent(),
            phrases: [
                "Show actionable setups in \(.applicationName)",
                "Open \(.applicationName) radar",
                "Show my trading setups in \(.applicationName)",
                "What's actionable in \(.applicationName)"
            ],
            shortTitle: "Show Actionable Setups",
            systemImageName: "antenna.radiowaves.left.and.right"
        )

        AppShortcut(
            intent: ExplainSetupIntent(),
            phrases: [
                "Explain \(\.$ticker) in \(.applicationName)",
                "Analyze \(\.$ticker) setup in \(.applicationName)",
                "Why is \(\.$ticker) in shadow in \(.applicationName)"
            ],
            shortTitle: "Explain Setup",
            systemImageName: "sparkles"
        )

        AppShortcut(
            intent: CopyTicketIntent(),
            phrases: [
                "Copy \(\.$ticker) ticket in \(.applicationName)",
                "Copy trade ticket for \(\.$ticker) in \(.applicationName)"
            ],
            shortTitle: "Copy Ticket",
            systemImageName: "doc.on.doc"
        )
    }
}
