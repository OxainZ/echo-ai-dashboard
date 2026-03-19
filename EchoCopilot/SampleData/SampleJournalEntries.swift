// SampleData/SampleJournalEntries.swift
// Echo Copilot — Sample journal entries for development and preview

import Foundation

enum SampleJournalEntries {
    static var all: [JournalEntry] { [nvdaWin, tslaLoss, metaOpen] }

    // Winning trade: NVDA +2.1R
    static let nvdaWin = JournalEntry(
        ticker: "NVDA",
        entryDate: Calendar.current.date(byAdding: .day, value: -3, to: Date()) ?? Date(),
        exitDate: Calendar.current.date(byAdding: .day, value: -2, to: Date()),
        entryPrice: 480.00,
        exitPrice: 499.50,
        stopPrice: 470.50,
        target1: 495.00,
        target2: 510.00,
        notes: "Clean breakout of PMH. Scaled at T1, trailed stop to entry. Final exit near T2.",
        tags: ["breakout", "earnings", "main-lane", "winner"]
    )

    // Losing trade: TSLA -0.8R
    static let tslaLoss = JournalEntry(
        ticker: "TSLA",
        entryDate: Calendar.current.date(byAdding: .day, value: -7, to: Date()) ?? Date(),
        exitDate: Calendar.current.date(byAdding: .day, value: -7, to: Date()),
        entryPrice: 244.00,
        exitPrice: 236.80,
        stopPrice: 232.00,
        target1: 258.00,
        target2: 268.00,
        notes: "Entered trigger on PMH break. Market reversed hard on macro news. Stopped out at -0.8R, which was above hard stop. Good exit.",
        tags: ["breakout", "main-lane", "loser", "macro-risk"]
    )

    // Open/ongoing trade: META
    static let metaOpen = JournalEntry(
        ticker: "META",
        entryDate: Calendar.current.date(byAdding: .hour, value: -2, to: Date()) ?? Date(),
        exitDate: nil,
        entryPrice: 515.20,
        exitPrice: nil,
        stopPrice: 500.00,
        target1: 522.00,
        target2: 530.00,
        notes: "Entered on PMH trigger. Still in trade. Stop moved to breakeven at 515.",
        tags: ["micro-lane", "ai-catalyst", "open"]
    )
}
