// Views/Journal/JournalListView.swift
// Echo Copilot — Journal entries list with stats bar and swipe-to-delete

import SwiftUI

struct JournalListView: View {
    @EnvironmentObject private var env: AppEnvironment
    @State private var vm: JournalListViewModel?
    @State private var showingEditor = false

    var body: some View {
        NavigationStack {
            Group {
                if let vm = vm {
                    JournalListContent(vm: vm)
                } else {
                    ProgressView()
                }
            }
            .navigationTitle("Journal")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showingEditor = true
                    } label: {
                        Image(systemName: "plus")
                    }
                }
            }
            .sheet(isPresented: $showingEditor) {
                JournalEditorView()
                    .environmentObject(env)
                    .onDisappear { vm?.load() }
            }
        }
        .onAppear {
            if vm == nil {
                let newVM = JournalListViewModel(repository: env.journalRepository)
                newVM.load()
                vm = newVM
            }
        }
    }
}

private struct JournalListContent: View {
    @Bindable var vm: JournalListViewModel

    var body: some View {
        VStack(spacing: 0) {
            // Stats bar
            if !vm.entries.isEmpty {
                HStack(spacing: 20) {
                    StatChip(label: "P&L", value: vm.totalPnL.asCurrency,
                              color: vm.totalPnL >= 0 ? .green : .red)
                    if let avgR = vm.averageR {
                        StatChip(label: "Avg R", value: String(format: "%.2fR", avgR),
                                  color: avgR >= 0 ? .cyan : .orange)
                    }
                    if let wr = vm.winRate {
                        StatChip(label: "Win%", value: "\(Int(wr * 100))%",
                                  color: wr >= 0.5 ? .green : .orange)
                    }
                    Spacer()
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 8)

                Divider()
            }

            if vm.entries.isEmpty {
                EmptyStateView(
                    systemImage: "book.closed",
                    title: "No Journal Entries",
                    subtitle: "Tap + to add your first trade."
                )
            } else {
                List {
                    if !vm.openTrades.isEmpty {
                        Section("Open Trades") {
                            ForEach(vm.openTrades) { entry in
                                NavigationLink(destination: JournalDetailView(entry: entry)) {
                                    JournalRowView(entry: entry)
                                }
                                .listRowBackground(Color.clear)
                            }
                            .onDelete { vm.delete(at: $0) }
                        }
                    }

                    if !vm.closedTrades.isEmpty {
                        Section("Closed Trades") {
                            ForEach(vm.closedTrades) { entry in
                                NavigationLink(destination: JournalDetailView(entry: entry)) {
                                    JournalRowView(entry: entry)
                                }
                                .listRowBackground(Color.clear)
                            }
                            .onDelete { vm.delete(at: $0) }
                        }
                    }
                }
                .listStyle(.insetGrouped)
            }
        }
    }
}

// MARK: - Journal row

private struct JournalRowView: View {
    let entry: JournalEntry

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 3) {
                Text(entry.ticker.uppercased())
                    .font(.headline)
                Text(entry.entryDate.asDateString)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            VStack(alignment: .trailing, spacing: 3) {
                if let pnl = entry.pnlDollars {
                    Text(pnl >= 0 ? "+\(pnl.asCurrency)" : pnl.asCurrency)
                        .font(.subheadline.bold().monospacedDigit())
                        .foregroundStyle(pnl >= 0 ? .green : .red)
                } else {
                    Text("Open")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.cyan)
                }

                if let r = entry.pnlR {
                    Text(String(format: r >= 0 ? "+%.2fR" : "%.2fR", r))
                        .font(.caption.monospacedDigit())
                        .foregroundStyle(r >= 0 ? .green : .orange)
                }
            }
        }
    }
}

// MARK: - Stat chip

private struct StatChip: View {
    let label: String
    let value: String
    let color: Color

    var body: some View {
        VStack(spacing: 1) {
            Text(label)
                .font(.system(size: 9))
                .foregroundStyle(.secondary)
            Text(value)
                .font(.system(size: 13, weight: .bold, design: .monospaced))
                .foregroundStyle(color)
        }
    }
}

#Preview {
    JournalListView()
        .environmentObject(AppEnvironment.preview)
        .preferredColorScheme(.dark)
}
