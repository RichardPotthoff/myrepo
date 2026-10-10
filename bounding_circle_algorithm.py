import cmath
import math
import random

class SubPath:
    def __init__(self, arcs=None):
        """
        arcs: List of tuples (l, dtheta)
        """
        self.arcs = arcs if arcs is not None else []
        # Cached properties (all defined in the LOCAL coordinate space where start is 0j and heading is 1+0j)
        self.delta_pos = 0j
        self.delta_heading = 1+0j
        self.local_center = 0j
        self.radius = 0.0
        self.supports = []  # Critical boundary points/arcs relative to local start
        
        if self.arcs:
            self._compute_and_cache()

    def _compute_and_cache(self):
        """
        Computes the path geometry and finds the minimum enclosing circle 
        using discrete boundary sampling of the continuous smooth arc path.
        """
        current_pos = 0j
        current_heading = 1+0j
        
        # We sample critical geometric points along the smooth path to represent it.
        # Thanks to G1 continuity, we only need endpoints and local directional peaks.
        sample_points = [current_pos]
        
        for l, dtheta in self.arcs:
            if abs(dtheta) < 1e-9:
                # Straight line segment
                current_pos += l * current_heading
                sample_points.append(current_pos)
            else:
                # Circular arc segment
                r = l / dtheta
                # Center is perpendicular to the heading (left turn if dtheta > 0)
                center = current_pos + (current_heading * 1j) * r
                
                # Sample endpoints and axis-aligned extrema along the arc
                start_angle = cmath.phase(-1j * current_heading) if dtheta > 0 else cmath.phase(1j * current_heading)
                
                # Update to end state
                current_heading *= cmath.exp(1j * dtheta)
                current_pos = center - (current_heading * 1j) * r if dtheta > 0 else center + (current_heading * 1j) * r
                sample_points.append(current_pos)
                
                # Check for extreme directional crowns (0, 90, 180, 270 degrees)
                # For smooth paths, sampling the midpoint of highly curved segments is a highly robust proxy
                if abs(dtheta) > math.pi / 2:
                    mid_heading = current_heading * cmath.exp(-1j * dtheta / 2)
                    mid_pos = center - (mid_heading * 1j) * r if dtheta > 0 else center + (mid_heading * 1j) * r
                    sample_points.append(mid_pos)

        self.delta_pos = current_pos
        self.delta_heading = current_heading
        
        # Run Welzl's algorithm on the representative points
        self.local_center, self.radius = self._welzl_points(sample_points)
        
        # Store the support points that define this boundary
        self.supports = [p for p in sample_points if abs(abs(p - self.local_center) - self.radius) < 1e-7]

    def _welzl_points(self, points):
        """Standard Welzl's algorithm for smallest enclosing circle of points."""
        P = points.copy()
        random.shuffle(P)
        return self._welzl_recurse(P, [], len(P))

    def _welzl_recurse(self, P, R, n):
        if n == 0 or len(R) == 3:
            return self._mec_base_case(R)
        
        p = P[n - 1]
        center, r = self._welzl_recurse(P, R, n - 1)
        
        if abs(p - center) <= r + 1e-7:
            return center, r
        
        return self._welzl_recurse(P, R + [p], n - 1)

    def _mec_base_case(self, R):
        if not R:
            return 0j, 0.0
        if len(R) == 1:
            return R[0], 0.0
        if len(R) == 2:
            center = (R[0] + R[1]) / 2.0
            return center, abs(R[0] - R[1]) / 2.0
        
        # 3 points: Circumcircle using complex number algebra
        z1, z2, z3 = R[0], R[1], R[2]
        w = (z3 - z1) / (z2 - z1)
        if abs(w.imag) < 1e-9:  # Collinear points
            # Fallback to max distance pair
            dists = [(abs(z1-z2), (z1+z2)/2), (abs(z2-z3), (z2+z3)/2), (abs(z3-z1), (z3+z1)/2)]
            max_d, c = max(dists, key=lambda x: x[0])
            return c, max_d / 2.0
        
        num = z1 * (w.real - abs(w)**2) + z2 * abs(w)**2 * (1 - w.real)
        den = 2j * w.imag * (z1 - z2).imag # Simplified determinant form
        # Standard geometric intersection formulation:
        # (z2-z1) perpendicular bisector crossed with (z3-z1) perpendicular bisector
        d = 2 * (z1.real * (z2.imag - z3.imag) + z2.real * (z3.imag - z1.imag) + z3.real * (z1.imag - z2.imag))
        if abs(d) < 1e-9:
            dists = [(abs(z1-z2), (z1+z2)/2), (abs(z2-z3), (z2+z3)/2), (abs(z3-z1), (z3+z1)/2)]
            max_d, c = max(dists, key=lambda x: x[0])
            return c, max_d / 2.0
            
        ux = ((z1.real**2 + z1.imag**2) * (z2.imag - z3.imag) + (z2.real**2 + z2.imag**2) * (z3.imag - z1.imag) + (z3.real**2 + z3.imag**2) * (z1.imag - z2.imag)) / d
        uy = ((z1.real**2 + z1.imag**2) * (z3.real - z2.real) + (z2.real**2 + z2.imag**2) * (z1.real - z3.real) + (z3.real**2 + z3.imag**2) * (z2.real - z1.real)) / d
        center = complex(ux, uy)
        return center, abs(z1 - center)


def compute_global_bounding_circle(sub_paths):
    """
    Computes the global bounding circle given a chain of pre-computed SubPaths.
    Runs in O(m) time where m is the number of sub-paths, utilizing ONLY the 
    cached boundary supports of the sub-paths transformed into global space.
    """
    if not sub_paths:
        return 0j, 0.0
        
    global_points_to_check = []
    
    # Track the current coordinate frame state as we chain the paths together
    current_global_origin = 0j
    current_global_heading = 1+0j
    
    for sp in sub_paths:
        # Transform this sub-path's cached boundary-defining support points 
        # into the running global coordinate frame.
        for local_sup in sp.supports:
            global_sup = current_global_origin + local_sup * current_global_heading
            global_points_to_check.append(global_sup)
            
        # Move the global frame state to the end of this sub-path
        current_global_origin += sp.delta_pos * current_global_heading
        current_global_heading *= sp.delta_heading

    # Run Welzl's algorithm purely on the tiny pool of critical support elements
    # Instead of re-evaluating thousands of raw arcs, we only evaluate ~3 * m points.
    dummy_path = SubPath()
    global_center, global_radius = dummy_path._welzl_points(global_points_to_check)
    
    return global_center, global_radius

class PathBVHNode:
    def __init__(self, sub_paths=None, global_origin=0j, global_heading=1+0j):
        """
        Builds a bounding volume node recursively.
        sub_paths: A list of SubPath objects that form a continuous sequence.
        global_origin / global_heading: The coordinate frame mapping this node's
                                        start point to the global arena.
        """
        self.left = None
        self.right = None
        self.sub_path = None  # Only populated if it's a leaf node
        
        # Absolute global coordinate frame for the start of this node's path segment
        self.origin = global_origin
        self.heading = global_heading
        
        if sub_paths is None or len(sub_paths) == 0:
            self.center = 0j
            self.radius = 0.0
            return
            
        if len(sub_paths) == 1:
            # Leaf node: Wraps a single SubPath
            self.sub_path = sub_paths[0]
            # Transform local cached center to global space
            self.center = self.origin + self.sub_path.local_center * self.heading
            self.radius = self.sub_path.radius
        else:
            # Internal node: Split the sub-path sequence down the middle
            mid = len(sub_paths) // 2
            left_paths = sub_paths[:mid]
            right_paths = sub_paths[mid:]
            
            # Left child shares the same starting frame as this node
            self.left = PathBVHNode(left_paths, self.origin, self.heading)
            
            # Compute where the right child's coordinate frame begins
            right_origin = self.origin
            right_heading = self.heading
            for sp in left_paths:
                right_origin += sp.delta_pos * right_heading
                right_heading *= sp.delta_heading
                
            self.right = PathBVHNode(right_paths, right_origin, right_heading)
            
            # Combine the bounding circles of the two children
            self._combine_child_bounds()

    def _combine_child_bounds(self):
        """Computes a bounding circle that encloses both child nodes."""
        c1, r1 = self.left.center, self.left.radius
        c2, r2 = self.right.center, self.right.radius
        
        dist = abs(c1 - c2)
        
        if dist + r1 <= r2:
            self.center, self.radius = c2, r2
        elif dist + r2 <= r1:
            self.center, self.radius = c1, r1
        else:
            # Standard analytical solution for enclosing two circles
            self.radius = (dist + r1 + r2) / 2.0
            if dist > 1e-9:
                self.center = c1 + ((c2 - c1) / dist) * (self.radius - r1)
            else:
                self.center = c1

    def is_leaf(self):
        return self.sub_path is not None


def find_nearest_point_on_path(node, target, best_dist=float('inf'), best_info=None):
    """
    Performs a branch-and-bound traversal to find the absolute closest point.
    target: The complex number representing the cursor coordinate.
    best_info: Dict tracking {'point': complex, 'arc_idx': int, 'subpath': SubPath}
    """
    # 1. Pruning Step: Check distance to this node's overall bounding circle
    dist_to_bound = abs(target - node.center) - node.radius
    if dist_to_bound >= best_dist:
        return best_dist, best_info  # Completely prune this branch

    # 2. Leaf Base Case: Evaluate underlying raw arcs using local complex coordinates
    if node.is_leaf():
        local_target = (target - node.origin) / node.heading
        local_pos = 0j
        local_heading = 1+0j
        
        for idx, (l, dtheta) in enumerate(node.sub_path.arcs):
            # Calculate the closest point on this specific arc element
            if abs(dtheta) < 1e-9:
                # Straight line projection
                segment_vec = l * local_heading
                # Project target onto line segment using vector dot product via complex numbers
                # dot(a, b) = (a * b.conjugate()).real
                t = ((local_target - local_pos) * local_heading.conjugate()).real / l
                t = max(0.0, min(1.0, t))
                closest_local = local_pos + t * segment_vec
                next_pos = local_pos + segment_vec
                next_heading = local_heading
            else:
                # Circular arc projection
                r = l / dtheta
                center = local_pos + (local_heading * 1j) * r
                
                # Vector from arc center to local target
                to_target = local_target - center
                if abs(to_target) > 1e-9:
                    closest_local = center + (to_target / abs(to_target)) * abs(r)
                else:
                    closest_local = local_pos  # Fallback if exactly at center
                
                # Clamp the point to the actual angular window span of the arc
                start_phase = cmath.phase(local_pos - center)
                closest_phase = cmath.phase(closest_local - center)
                
                # Normalize angles relative to start_phase based on direction
                angle_diff = closest_phase - start_phase
                if dtheta > 0:
                    if angle_diff < 0: angle_diff += 2 * math.pi
                    if angle_diff > dtheta:
                        closest_local = local_pos if angle_diff > (dtheta + math.pi) else center + (local_pos - center) * cmath.exp(1j * dtheta)
                else:
                    if angle_diff > 0: angle_diff -= 2 * math.pi
                    if angle_diff < dtheta:
                        closest_local = local_pos if angle_diff < (dtheta - math.pi) else center + (local_pos - center) * cmath.exp(1j * dtheta)
                
                # Move state to the end of the arc
                next_heading = local_heading * cmath.exp(1j * dtheta)
                next_pos = center - (next_heading * 1j) * r if dtheta > 0 else center + (next_heading * 1j) * r
            
            # Map the local closest point back to global space
            global_closest = node.origin + closest_local * node.heading
            current_dist = abs(target - global_closest)
            
            if current_dist < best_dist:
                best_dist = current_dist
                best_info = {
                    'point': global_closest,
                    'arc': (l, dtheta),
                    'arc_idx': idx,
                    'subpath': node.sub_path
                }
                
            local_pos = next_pos
            local_heading = next_heading
            
        return best_dist, best_info

    # 3. Internal Node Traversal: Prioritize the closer bounding circle child first
    dist_l = abs(target - node.left.center) - node.left.radius
    dist_r = abs(target - node.right.center) - node.right.radius
    
    if dist_l < dist_r:
        best_dist, best_info = find_nearest_point_on_path(node.left, target, best_dist, best_info)
        best_dist, best_info = find_nearest_point_on_path(node.right, target, best_dist, best_info)
    else:
        best_dist, best_info = find_nearest_point_on_path(node.right, target, best_dist, best_info)
        best_dist, best_info = find_nearest_point_on_path(node.left, target, best_dist, best_info)
        
    return best_dist, best_info


# --- Example Usage & Validation ---
if __name__ == "__main__":
    # Create Sub-path 1: A large sweeping left turn (radius ~10)
    # 3 continuous segments making up a smooth arc sequence
    sp1 = SubPath([
        (5.0, 0.5),   # arc length 5, turns 0.5 rad
        (10.0, 0.0),  # straight line for 10 units
        (5.0, 0.5)    # arc length 5, turns 0.5 rad
    ])
    
    # Create Sub-path 2: A tight right-hand spiral loop
    sp2 = SubPath([
        (2.0, -0.8),
        (2.0, -1.2),
        (1.0, -1.5)
    ])
    
    print(f"Sub-path 1 Local Bounding Circle: Center={sp1.local_center}, Radius={sp1.radius:.2f}")
    print(f"Sub-path 2 Local Bounding Circle: Center={sp2.local_center}, Radius={sp2.radius:.2f}")
    
    # Combine them hierarchically using their caches
    global_center, global_radius = compute_global_bounding_circle([sp1, sp2])
    print(f"\nGlobal Enclosing Circle: Center={global_center}, Radius={global_radius:.2f}")

