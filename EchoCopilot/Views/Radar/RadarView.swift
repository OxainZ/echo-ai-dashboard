// Views/Radar/RadarView.swift
// Echo Copilot — Radar tab: searchable setup list with filter chips and sort control

import SwiftUI

struct RadarView: View {
    @EnvironmentObject private var env: AppEnvironment
    @State private var viewModel: RadarViewModel?

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
            }
        }
        .task {
            let settings = env.settingsRepository.load()
            let vm = RadarViewModel(repository: env.setupRepository, settings: settings)
            viewModel = vm
            await vm.load()
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
                    subtitle: "No setups match your current filter."
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
                    }
                }
                .listStyle(.plain)
                .refreshable {
                    await vm.refresh()
                }
            }
        }
        .searchable(text: $vm.searchText, prompt: "Search ticker or company")
    }
}

#Preview {
    RadarView()
        .environmentObject(AppEnvironment.preview)
        .preferredColorScheme(.dark)
}
