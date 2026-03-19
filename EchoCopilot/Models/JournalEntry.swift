// Models/JournalEntry.swift
// Echo Copilot — Trade journal entry model

import Foundation

struct JournalEntry: Identifiable, Codable, Hashable {
    var id: UUID
    var ticker: String
    var entryDate: Date
    var exitDate: Date?
    var entryPrice: Double
    var exitPrice: Double?
    var stopPrice: Double?
    var target1: Double?
    var target2: Double?
    var notes: String
    var tags: [String]
    // Screenshot stored as base64 string for UserDefaults persistence
    // Replace with file URL reference when using a database
    var screenshotBase64: String?

    init(
        id: UUID = UUID(),
        ticker: String,
        entryDate: Date = Date(),
        exitDate: Date? = nil,
        entryPrice: Double,
        exitPrice: Double? = nil,
        stopPrice: Double? = nil,
        target1: Double? = nil,
        target2: Double? = nil,
        notes: String = "",
        tags: [String] = [],
        screenshotBase64: String? = nil
    ) {
        self.id = id
        self.ticker = ticker
        self.entryDate = entryDate
        self.exitDate = exitDate
        self.entryPrice = entryPrice
        self.exitPrice = exitPrice
        self.stopPrice = stopPrice
        self.target1 = target1
        self.target2 = target2
        self.notes = notes
        self.tags = tags
        self.screenshotBase64 = screenshotBase64
    }

    // MARK: - Computed PnL

    /// Dollar P&L based on exit price. Nil if no exit price.
    var pnlDollars: Double? {
        guard let exit = exitPrice else { return nil }
        return exit - entryPrice
    }

    /// P&L expressed in R (risk units). Nil if stop or exit price missing.
    var pnlR: Double? {
        guard let exit = exitPrice, let stop = stopPrice else { return nil }
        let riskPerShare = abs(entryPrice - stop)
        guard riskPerShare > 0 else { return nil }
        return (exit - entryPrice) / riskPerShare
    }

    /// True if the trade was a winner (exit > entry for long).
    var isWinner: Bool? {
        guard let pnl = pnlDollars else { return nil }
        return pnl > 0
    }
}
