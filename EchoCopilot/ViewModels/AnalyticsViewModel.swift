// ViewModels/AnalyticsViewModel.swift
// Echo Copilot — Analytics: P&L curve, R distribution, win rate, drawdown

import Foundation
import Observation

enum AnalyticsDateRange: String, CaseIterable, Identifiable {
    case allTime   = "All Time"
    case thisWeek  = "This Week"
    case thisMonth = "This Month"
    case lastMonth = "Last Month"
    case thisYear  = "This Year"

    var id: String { rawValue }

    func startDate(calendar: Calendar = .current) -> Date? {
        let now = Date()
        switch self {
        case .allTime:   return nil
        case .thisWeek:  return calendar.date(from: calendar.dateComponents([.yearForWeekOfYear, .weekOfYear], from: now))
        case .thisMonth: return calendar.date(from: calendar.dateComponents([.year, .month], from: now))
        case .lastMonth:
            let comps = calendar.dateComponents([.year, .month], from: now)
            guard var month = comps.month, let year = comps.year else { return nil }
            month -= 1
            let adjusted = month < 1 ? DateComponents(year: year - 1, month: 12) : DateComponents(year: year, month: month)
            return calendar.date(from: adjusted)
        case .thisYear:  return calendar.date(from: calendar.dateComponents([.year], from: now))
        }
    }
}

@Observable
final class AnalyticsViewModel {
    var entries: [JournalEntry] = []
    var errorMessage: String? = nil
    var dateRange: AnalyticsDateRange = .allTime

    private let repository: any JournalRepositoryProtocol

    init(repository: any JournalRepositoryProtocol) {
        self.repository = repository
    }

    func load() {
        do {
            entries = try repository.fetchEntries()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    // MARK: - Filtered entries

    private var filteredEntries: [JournalEntry] {
        guard let start = dateRange.startDate() else { return entries }
        return entries.filter { ($0.exitDate ?? $0.entryDate) >= start }
    }

    // MARK: - Subsets

    var closedTrades: [JournalEntry] { filteredEntries.filter { $0.exitPrice != nil } }

    // MARK: - Summary stats

    var totalPnL: Double {
        closedTrades.compactMap { $0.pnlDollars }.reduce(0, +)
    }

    var winRate: Double? {
        guard !closedTrades.isEmpty else { return nil }
        let winners = closedTrades.filter { ($0.pnlDollars ?? 0) > 0 }
        return Double(winners.count) / Double(closedTrades.count)
    }

    var averageR: Double? {
        let rs = closedTrades.compactMap { $0.pnlR }
        guard !rs.isEmpty else { return nil }
        return rs.reduce(0, +) / Double(rs.count)
    }

    var bestTrade: JournalEntry? {
        closedTrades.max { ($0.pnlDollars ?? -.infinity) < ($1.pnlDollars ?? -.infinity) }
    }

    var worstTrade: JournalEntry? {
        closedTrades.min { ($0.pnlDollars ?? .infinity) < ($1.pnlDollars ?? .infinity) }
    }

    var maxDrawdown: Double {
        let points = cumulativePnLPoints
        guard !points.isEmpty else { return 0 }
        var peak = points[0].cumulativePnL
        var maxDD = 0.0
        for p in points {
            if p.cumulativePnL > peak { peak = p.cumulativePnL }
            let dd = peak - p.cumulativePnL
            if dd > maxDD { maxDD = dd }
        }
        return maxDD
    }

    // MARK: - P&L curve

    struct PnLPoint: Identifiable {
        let id: UUID
        let date: Date
        let cumulativePnL: Double
    }

    var cumulativePnLPoints: [PnLPoint] {
        let sorted = closedTrades
            .compactMap { entry -> (Date, Double, UUID)? in
                guard let exit = entry.exitDate, let pnl = entry.pnlDollars else { return nil }
                return (exit, pnl, entry.id)
            }
            .sorted { $0.0 < $1.0 }

        var running = 0.0
        return sorted.map { date, pnl, id in
            running += pnl
            return PnLPoint(id: id, date: date, cumulativePnL: running)
        }
    }

    // MARK: - R distribution

    struct RBucket: Identifiable {
        let id: String
        let label: String
        let count: Int
        let isWin: Bool
    }

    var rDistribution: [RBucket] {
        let rs = closedTrades.compactMap { $0.pnlR }
        guard !rs.isEmpty else { return [] }

        let buckets: [(String, ClosedRange<Double>, Bool)] = [
            ("< -2R",    -100.0 ... -2.0,   false),
            ("-2 to -1R", -2.0  ... -1.0,   false),
            ("-1 to 0R",  -1.0  ...  0.0,   false),
            ("0 to 1R",    0.0  ...  1.0,   true),
            ("1 to 2R",    1.0  ...  2.0,   true),
            ("> 2R",       2.0  ... 100.0,  true)
        ]

        return buckets.compactMap { label, range, isWin in
            let count = rs.filter { range.contains($0) }.count
            guard count > 0 else { return nil }
            return RBucket(id: label, label: label, count: count, isWin: isWin)
        }
    }
}
