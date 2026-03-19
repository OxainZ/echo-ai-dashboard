// Views/Journal/JournalDetailView.swift
// Echo Copilot — Read-only journal entry detail screen

import SwiftUI

struct JournalDetailView: View {
    let entry: JournalEntry
    @EnvironmentObject private var env: AppEnvironment
    @State private var showingEditor = false
    @State private var showingCloseSheet = false

    var body: some View {
        ScrollView {
            VStack(spacing: 14) {
                // Header
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(entry.ticker.uppercased())
                            .font(.largeTitle.bold())
                        Text(entry.entryDate.asDateTimeString)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                    if let pnl = entry.pnlDollars {
                        VStack(alignment: .trailing, spacing: 2) {
                            Text(pnl >= 0 ? "+\(pnl.asCurrency)" : pnl.asCurrency)
                                .font(.title2.bold().monospacedDigit())
                                .foregroundStyle(pnl >= 0 ? .green : .red)
                            if let r = entry.pnlR {
                                Text(String(format: r >= 0 ? "+%.2fR" : "%.2fR", r))
                                    .font(.caption.monospacedDigit())
                                    .foregroundStyle(r >= 0 ? .green : .orange)
                            }
                        }
                    } else {
                        Text("Open")
                            .font(.headline)
                            .foregroundStyle(.cyan)
                    }
                }
                .padding(14)
                .background(Color(.systemGray6), in: RoundedRectangle(cornerRadius: 14))

                // Trade details
                SectionCardView(title: "Trade Levels", systemImage: "chart.xyaxis.line") {
                    MetricRowView(label: "Entry Price", value: entry.entryPrice.asPrice)
                    if let stop = entry.stopPrice {
                        MetricRowView(label: "Stop Price", value: stop.asPrice,
                                      highlight: true, valueColor: .red)
                    }
                    if let exit = entry.exitPrice {
                        MetricRowView(label: "Exit Price", value: exit.asPrice,
                                      highlight: true, valueColor: exit >= entry.entryPrice ? .green : .red)
                    }
                    if let t1 = entry.target1 {
                        MetricRowView(label: "Target 1", value: t1.asPrice)
                    }
                    if let t2 = entry.target2 {
                        MetricRowView(label: "Target 2", value: t2.asPrice)
                    }
                }

                // Dates
                SectionCardView(title: "Timing", systemImage: "calendar") {
                    MetricRowView(label: "Entry Date", value: entry.entryDate.asDateTimeString)
                    if let exit = entry.exitDate {
                        MetricRowView(label: "Exit Date", value: exit.asDateTimeString)
                    }
                }

                // Tags
                if !entry.tags.isEmpty {
                    SectionCardView(title: "Tags", systemImage: "tag") {
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 6) {
                                ForEach(entry.tags, id: \.self) { tag in
                                    Text(tag)
                                        .font(.caption.weight(.medium))
                                        .padding(.horizontal, 10)
                                        .padding(.vertical, 4)
                                        .background(Color(.systemGray4), in: Capsule())
                                }
                            }
                        }
                    }
                }

                // Notes
                if !entry.notes.isEmpty {
                    SectionCardView(title: "Notes", systemImage: "note.text") {
                        Text(entry.notes)
                            .font(.subheadline)
                            .foregroundStyle(.primary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
            }
            .padding(16)
        }
        .navigationTitle(entry.ticker.uppercased())
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            if entry.exitPrice == nil {
                ToolbarItem(placement: .topBarLeading) {
                    Button {
                        showingCloseSheet = true
                    } label: {
                        Label("Close Trade", systemImage: "flag.checkered")
                            .foregroundStyle(.green)
                    }
                }
            }
            ToolbarItem(placement: .topBarTrailing) {
                Button("Edit") { showingEditor = true }
            }
        }
        .sheet(isPresented: $showingEditor) {
            JournalEditorView(editingEntry: entry)
                .environmentObject(env)
        }
        .sheet(isPresented: $showingCloseSheet) {
            CloseTradeView(entry: entry) { exitPrice, exitDate in
                var updated = entry
                updated.exitPrice = exitPrice
                updated.exitDate = exitDate
                try? env.journalRepository.update(entry: updated)
            }
            .environmentObject(env)
        }
    }
}

#Preview {
    NavigationStack {
        JournalDetailView(entry: JournalEntry.previewEntry)
            .environmentObject(AppEnvironment.preview)
            .preferredColorScheme(.dark)
    }
}
