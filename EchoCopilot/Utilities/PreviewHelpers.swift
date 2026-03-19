// Utilities/PreviewHelpers.swift
// Echo Copilot — Convenience factories for SwiftUI previews

import Foundation

extension TickerSetup {
    static var previewActionable: TickerSetup {
        TickerSetup(
            symbol: "NVDA",
            companyName: "NVIDIA Corporation",
            lane: .main,
            status: .actionable,
            price: 487.50,
            priorClose: 480.00,
            pmh: 491.00,
            pdh: 489.00,
            pdl: 475.00,
            trigger: 491.10,
            invalidation: 475.00,
            target1: 500.00,
            target2: 510.00,
            spreadPct: 0.18,
            rvol: 2.8,
            volZ: 2.1,
            dollarVolume: 4_200_000_000,
            adtvDollar: 2_800_000_000,
            impactPctADTV: 0.12,
            halted: false,
            ssrActive: false,
            cashCompliance: .cashOK,
            timestamp: Date(),
            notes: "Strong PM momentum on earnings beat",
            catalystSummary: "Q3 earnings beat + raised FY guidance",
            shadowReasons: [],
            isVerified: true
        )
    }

    static var previewShadow: TickerSetup {
        TickerSetup(
            symbol: "AAPL",
            companyName: "Apple Inc.",
            lane: .main,
            status: .shadow,
            price: 178.30,
            priorClose: 175.00,
            pmh: 179.00,
            pdh: 178.50,
            pdl: 172.00,
            trigger: nil,
            invalidation: 172.00,
            target1: nil,
            target2: nil,
            spreadPct: 0.22,
            rvol: 0.9,
            volZ: 0.4,
            halted: false,
            ssrActive: false,
            cashCompliance: .cashOK,
            timestamp: Date(),
            notes: "Watching for trigger confirmation",
            shadowReasons: [.missingTrigger, .missingTargets, .rvolTooLow, .volZTooLow],
            isVerified: false
        )
    }
}

extension JournalEntry {
    static var previewEntry: JournalEntry {
        JournalEntry(
            ticker: "NVDA",
            entryDate: Calendar.current.date(byAdding: .day, value: -3, to: Date()) ?? Date(),
            exitDate: Calendar.current.date(byAdding: .day, value: -2, to: Date()),
            entryPrice: 480.00,
            exitPrice: 499.50,
            stopPrice: 473.00,
            target1: 495.00,
            target2: 505.00,
            notes: "Clean breakout of PM high. Held through lunch dip.",
            tags: ["breakout", "earnings", "main-lane"]
        )
    }
}

extension AppSettings {
    static var preview: AppSettings { AppSettings() }
}

extension AppEnvironment {
    static var preview: AppEnvironment {
        AppEnvironment()
    }
}
