// Views/Radar/RadarView.swift
// Echo Copilot — Radar tab: searchable setup list with filter chips and sort control

import SwiftUI

struct RadarView: View {
    @EnvironmentObject private var env: AppEnvironment
    @State private var viewModel: RadarViewModel?
    @State private var showingNewSetup = false

    var body: some View {
        NavigationStack {
            Group {
                if let vm = viewModel {
                    RadarContentView(vm: vm)
                } else {
                    ProgressView()
                }
            }
            .navigationTitle("Radar")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                if let vm = viewModel {
                    ToolbarItem(placement: .topBarTrailing) {
                        sortMenu(vm: vm)
                    }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showingNewSetup = true
                    } label: {
                        Image(systemName: "plus")
                    }
                }
            }
        }
        .task {
            let settings = env.settingsRepository.load()
            let vm = RadarViewModel(repository: env.setupRepository, settings: settings)
            viewModel = vm
            await vm.load()
        }
        .sheet(isPresented: $showingNewSetup) {
            SetupEditorView()
                .environmentObject(env)
                .onDisappear { Task { await viewModel?.load() } }
        }
    }

    @ViewBuilder
    private func sortMenu(vm: RadarViewModel) -> some View {
        Menu {
            ForEach(SortOption.allCases) { option in
                Button {
                    vm.selectedSort = option
                } label: {
                    HStack {
                        Text(option.rawValue)
                        if vm.selectedSort == option {
                            Image(systemName: "checkmark")
                        }
                    }
                }
            }
        } label: {
            Image(systemName: "arrow.up.arrow.down")
        }
    }
}

// MARK: - Main content (separated so SwiftUI can track vm changes)

private struct RadarContentView: View {
    @Bindable var vm: RadarViewModel
    @EnvironmentObject private var env: AppEnvironment
    @State private var editingSetup: TickerSetup? = nil

    var body: some View {
        VStack(spacing: 0) {
            // Filter chips
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(RadarFilter.allCases) { filter in
                        FilterChipView(
                            title: filter.rawValue,
                            isSelected: vm.selectedFilter == filter
                        ) {
                            vm.selectedFilter = filter
                        }
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
            }

            // Refresh error banner
            if let banner = vm.refreshBanner {
                HStack(spacing: 6) {
                    Image(systemName: "wifi.exclamationmark").foregroundStyle(.orange)
                    Text(banner).font(.caption).foregroundStyle(.orange)
                    Spacer()
                    Button { vm.refreshBanner = nil } label: {
                        Image(systemName: "xmark").font(.caption2)
                    }
                    .foregroundStyle(.secondary)
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 6)
                .background(Color.orange.opacity(0.08))
            }

            // Stats bar
            if !vm.setups.isEmpty {
                HStack(spacing: 16) {
                    Label("\(vm.actionableCount) Actionable", systemImage: "checkmark.circle.fill")
                        .foregroundStyle(.green)
                    Label("\(vm.shadowCount) Shadow", systemImage: "exclamationmark.triangle.fill")
                        .foregroundStyle(.orange)
                    Spacer()
                }
                .font(.caption)
                .padding(.horizontal, 16)
                .padding(.bottom, 4)
            }

            Divider()

            // List
            if vm.isLoading {
                Spacer()
                ProgressView("Loading setups…")
                Spacer()
            } else if let error = vm.errorMessage {
                Spacer()
                EmptyStateView(
                    systemImage: "exclamationmark.triangle",
                    title: "Load Error",
                    subtitle: error
                )
                Spacer()
            } else if vm.displayedSetups.isEmpty {
                Spacer()
                EmptyStateView(
                    systemImage: "antenna.radiowaves.left.and.right",
                    title: "No Setups",
                    subtitle: vm.searchText.isEmpty
                        ? "Tap + to add your first setup."
                        : "No results for '\(vm.searchText)'."
                )
                Spacer()
            } else {
                List {
                    ForEach(vm.displayedSetups) { setup in
                        NavigationLink(destination: SetupDetailView(setup: setup)) {
                            SetupCardView(setup: setup)
                                .listRowInsets(EdgeInsets())
                        }
                        .listRowBackground(Color.clear)
                        .listRowSeparator(.hidden)
                        .padding(.vertical, 4)
                        .padding(.horizontal, 12)
                        .swipeActions(edge: .leading) {
                            Button {
                                editingSetup = setup
                            } label: {
                                Label("Edit", systemImage: "pencil")
                            }
                            .tint(.blue)
                        }
                        .swipeActions(edge: .trailing, allowsFullSwipe: true) {
                            Button(role: .destructive) {
                                Task {
                                    try? await env.setupRepository.delete(id: setup.id)
                                    await vm.load()
                                }
                            } label: {
                                Label("Delete", systemImage: "trash")
                            }
                        }
                    }
                }
                .listStyle(.plain)
                .refreshable {
                    await vm.refresh()
                }
            }
        }
        .searchable(text: $vm.searchText, prompt: "Search ticker or company")
        .sheet(item: $editingSetup) { setup in
            SetupEditorView(editing: setup)
                .environmentObject(env)
                .onDisappear { Task { await vm.load() } }
        }
    }
}

#Preview {
    RadarView()
        .environmentObject(AppEnvironment.preview)
        .preferredColorScheme(.dark)
}
