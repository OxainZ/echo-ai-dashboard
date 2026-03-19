// Intents/CopyTicketIntent.swift
// Echo Copilot — App Intent: copy the trade ticket for a given ticker to the clipboard

import AppIntents
import UIKit

struct CopyTicketIntent: AppIntent {
    static let title: LocalizedStringResource = "Copy Trade Ticket"
    static let description = IntentDescription("Copies the formatted trade ticket for the given ticker to the clipboard.")

    @Parameter(title: "Ticker Symbol")
    var ticker: String

    static let openAppWhenRun: Bool = false

    func perform() async throws -> some ProvidesDialog {
        let repo = UserDefaultsSetupRepository()
        let setups = try await repo.fetchSetups()

        guard let setup = setups.first(where: { $0.symbol.uppercased() == ticker.uppercased() }) else {
            return .result(dialog: "No setup found for \(ticker).")
        }

        let ticket = CopyTicketService().ticketText(for: setup)

        // Copy on main actor
        await MainActor.run {
            UIPasteboard.general.string = ticket
        }

        return .result(dialog: "Trade ticket for \(ticker) copied to clipboard.")
    }
}
