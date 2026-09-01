import app.freerouting.board.BoardObservers;
import app.freerouting.board.Component;
import app.freerouting.board.Item;
import app.freerouting.board.ItemIdentificationNumberGenerator;
import app.freerouting.board.Pin;
import app.freerouting.board.RoutingBoard;
import app.freerouting.core.RoutingJob;
import app.freerouting.drc.AirLine;
import app.freerouting.drc.ClearanceViolation;
import app.freerouting.drc.DesignRulesChecker;
import app.freerouting.io.specctra.DsnWriter;
import app.freerouting.management.HeadlessBoardManager;
import app.freerouting.settings.DesignRulesCheckerSettings;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** DRC summary and deterministic handoff helpers for a Specctra DSN checkpoint. */
public final class FreeroutingAudit {
  private static final BoardObservers NO_OP_OBSERVERS = new BoardObservers() {
    private boolean active;

    @Override public void notify_deleted(Item item) {}
    @Override public void notify_changed(Item item) {}
    @Override public void notify_new(Item item) {}
    @Override public void notify_moved(Component component) {}
    @Override public void activate() { active = true; }
    @Override public void deactivate() { active = false; }
    @Override public boolean is_active() { return active; }
  };

  private static String describe(Item item) {
    if (item == null) return "<none>";
    String component = item.component_name();
    return item + " component=" + (component == null ? "<none>" : component)
      + " nets=" + item.getAllNetNames();
  }

  private static int find(Map<Integer, Integer> parent, int value) {
    int root = value;
    while (parent.get(root) != root) root = parent.get(root);
    while (value != root) {
      int next = parent.get(value);
      parent.put(value, root);
      value = next;
    }
    return root;
  }

  private static void union(Map<Integer, Integer> parent, int first, int second) {
    int firstRoot = find(parent, first);
    int secondRoot = find(parent, second);
    if (firstRoot != secondRoot) parent.put(secondRoot, firstRoot);
  }

  private static int netNameRank(String name) {
    if (name == null) return 3;
    if (name.contains("_source_net_")) return 0;
    if (!name.startsWith("Net-(")) return 1;
    return 2;
  }

  /**
   * Specctra requires one electrical net ID per physical junction. The
   * tscircuit DSN exporter can emit several implicit net IDs when multiple
   * point-to-point source traces meet on one pin. Union exactly those IDs;
   * unrelated nets are never combined.
   */
  private static int normalizeSharedPinNets(RoutingBoard board) {
    Map<Integer, Integer> parent = new HashMap<>();
    int maxNet = board.rules.nets.max_net_no();
    for (int net = 1; net <= maxNet; net++) parent.put(net, net);

    for (Pin pin : board.get_pins()) {
      if (pin.net_count() < 2) continue;
      int first = pin.get_net_no(0);
      for (int i = 1; i < pin.net_count(); i++) {
        union(parent, first, pin.get_net_no(i));
      }
    }

    Map<Integer, List<Integer>> groups = new HashMap<>();
    for (int net = 1; net <= maxNet; net++) {
      groups.computeIfAbsent(find(parent, net), ignored -> new ArrayList<>()).add(net);
    }

    Map<Integer, Integer> canonicalByNet = new HashMap<>();
    int mergedNetCount = 0;
    for (List<Integer> group : groups.values()) {
      if (group.size() < 2) continue;
      group.sort(
        Comparator
          .comparingInt((Integer number) -> netNameRank(board.rules.nets.get(number).name))
          .thenComparing(number -> board.rules.nets.get(number).name)
          .thenComparingInt(Integer::intValue)
      );
      int canonical = group.get(0);
      for (int net : group) canonicalByNet.put(net, canonical);
      mergedNetCount += group.size() - 1;
      System.out.printf(
        "NET_UNION\tcanonical=%s\tmembers=%s%n",
        board.rules.nets.get(canonical).name,
        group.stream().map(number -> board.rules.nets.get(number).name).toList()
      );
    }

    int assignmentChanges = 0;
    for (Item item : new ArrayList<>(board.get_items())) {
      List<Integer> oldNets = new ArrayList<>();
      Set<Integer> desiredNets = new HashSet<>();
      for (int i = 0; i < item.net_count(); i++) {
        int oldNet = item.get_net_no(i);
        oldNets.add(oldNet);
        desiredNets.add(canonicalByNet.getOrDefault(oldNet, oldNet));
      }
      for (int oldNet : oldNets) {
        int desiredNet = canonicalByNet.getOrDefault(oldNet, oldNet);
        if (desiredNet == oldNet) continue;
        if (item.remove_from_net(oldNet)) assignmentChanges++;
      }
      for (int desiredNet : desiredNets) {
        boolean present = false;
        for (int i = 0; i < item.net_count(); i++) {
          if (item.get_net_no(i) == desiredNet) {
            present = true;
            break;
          }
        }
        if (!present) item.assign_net_no(desiredNet);
      }
    }
    board.reduce_nets_of_route_items();
    System.out.printf(
      "NORMALIZED\tmerged_nets=%d\tassignment_changes=%d%n",
      mergedNetCount,
      assignmentChanges
    );
    return mergedNetCount;
  }

  public static void main(String[] args) throws Exception {
    if (args.length < 1 || args.length % 2 == 0) {
      System.err.println(
        "usage: FreeroutingAudit <routed.dsn>"
          + " [--normalize-output <normalized.dsn>]"
          + " [--ses-output <routed.ses>]"
          + " [--base-design <design.dsn>]"
      );
      System.exit(2);
    }

    Path normalizedOutput = null;
    Path sesOutput = null;
    String baseDesign = null;
    for (int i = 1; i < args.length; i += 2) {
      switch (args[i]) {
        case "--normalize-output" -> normalizedOutput = Path.of(args[i + 1]).toAbsolutePath();
        case "--ses-output" -> sesOutput = Path.of(args[i + 1]).toAbsolutePath();
        case "--base-design" -> baseDesign = args[i + 1];
        default -> throw new IllegalArgumentException("unknown option: " + args[i]);
      }
    }

    Path input = Path.of(args[0]).toAbsolutePath();
    RoutingJob job = new RoutingJob();
    HeadlessBoardManager manager = new HeadlessBoardManager(job);
    try (FileInputStream stream = new FileInputStream(input.toFile())) {
      Object result = manager.loadFromSpecctraDsn(
        stream,
        NO_OP_OBSERVERS,
        new ItemIdentificationNumberGenerator()
      );
      if (result == null) throw new IllegalStateException("DSN parser returned no result");
    }

    RoutingBoard board = manager.get_routing_board();
    if (board == null) throw new IllegalStateException("DSN did not produce a routing board");

    if (normalizedOutput != null) normalizeSharedPinNets(board);

    DesignRulesCheckerSettings settings = new DesignRulesCheckerSettings();
    settings.enabled = true;
    settings.includeErrors = true;
    settings.includeWarnings = true;
    DesignRulesChecker checker = new DesignRulesChecker(board, settings);
    checker.calculateAllIncompletes();

    int multiNetPinCount = 0;
    for (Pin pin : board.get_pins()) {
      if (pin.net_count() <= 1) continue;
      multiNetPinCount++;
      System.out.printf(
        "MULTI_NET_PIN\tcomponent=%s\tpin=%s\tnets=%s%n",
        pin.component_name(),
        pin.name(),
        pin.getAllNetNames()
      );
    }
    System.out.println("MULTI_NET_PINS\t" + multiNetPinCount);

    AirLine[] airLines = checker.getAllAirlines();
    System.out.println("UNROUTED\t" + airLines.length);
    for (int i = 0; i < airLines.length; i++) {
      AirLine line = airLines[i];
      System.out.printf(
        "AIRWIRE\t%d\tnet=%s\tfrom=%s\tto=%s\tfrom_xy=%s\tto_xy=%s%n",
        i + 1,
        line.net.name,
        describe(line.from_item),
        describe(line.to_item),
        line.from_corner,
        line.to_corner
      );
    }

    Collection<ClearanceViolation> violations = checker.getAllClearanceViolations();
    System.out.println("CLEARANCE_VIOLATIONS\t" + violations.size());
    int sameNetViolations = 0;
    int crossNetViolations = 0;
    int sameComponentViolations = 0;
    int index = 0;
    for (ClearanceViolation violation : violations) {
      if (violation.first_item.shares_net(violation.second_item)) {
        sameNetViolations++;
      } else {
        crossNetViolations++;
      }
      int firstComponent = violation.first_item.get_component_no();
      if (firstComponent > 0 && firstComponent == violation.second_item.get_component_no()) {
        sameComponentViolations++;
      }
      System.out.printf(
        "CLEARANCE\t%d\tlayer=%d\texpected=%.3f\tactual=%.3f\tfirst=%s\tsecond=%s%n",
        ++index,
        violation.layer,
        violation.expected_clearance,
        violation.actual_clearance,
        describe(violation.first_item),
        describe(violation.second_item)
      );
    }
    System.out.printf(
      "CLEARANCE_SUMMARY\tsame_net=%d\tcross_net=%d\tsame_component=%d%n",
      sameNetViolations,
      crossNetViolations,
      sameComponentViolations
    );

    if (normalizedOutput != null) {
      try (FileOutputStream stream = new FileOutputStream(normalizedOutput.toFile())) {
        DsnWriter.write(
          board,
          stream,
          normalizedOutput.getFileName().toString(),
          false
        );
      }
      System.out.println("WROTE_NORMALIZED_DSN\t" + normalizedOutput);
    }

    if (sesOutput != null) {
      String sessionBaseDesign = baseDesign == null ? input.getFileName().toString() : baseDesign;
      try (FileOutputStream stream = new FileOutputStream(sesOutput.toFile())) {
        if (!manager.saveAsSpecctraSessionSes(stream, sessionBaseDesign)) {
          throw new IllegalStateException("Specctra session writer reported failure");
        }
      }
      System.out.printf(
        "WROTE_SESSION\t%s\tbase_design=%s%n",
        sesOutput,
        sessionBaseDesign
      );
    }
  }
}
