import numpy as np
import matplotlib.pyplot as plt
import cmath
rad=(-1)**(1/cmath.pi)
def compute_biarc_p(P: complex, w0: float) -> float:
    """
    Computes the biarc family parameter p for a given point P (x + iy) 
    and lens half-width angle w0 according to Equation (33).
    """
    # 1. Phase angle of the lens as a complex unit vector
    E2 = rad**(2* w0)
    
    # 2. Conformal Möbius mapping to the W-plane
    W = (P - 1) / (P + 1)
    
    # 3. Branch execution based on the sign of the imaginary part
    if P.imag >= 0:
        p_complex = (1 - E2) / (E2 * W - W.conjugate())
    else:
        p_complex = (E2 * (1 / W) - (1 / W.conjugate())) / (1 - E2)
        
    # The result is strictly a real number; extract the real part
    return p_complex.real
    
import cmath

def calculate_biarc_geometry_complex(p: float, Ta: complex, Tb: complex):
    """
    Calculates the biarc geometry using purely complex vector math.
    
    Inputs:
        p: family parameter (float)
        Ta: complex unit vector of the start tangent (e^(i*alpha0))
        Tb: complex unit vector of the end tangent (e^(i*beta0))
    """
    # --- 1. Compute the Complex Junction Point J ---
    # In complex terms, Kurnosenko's lens bisector phasor is sqrt(Ta * Tb.conjugate())
    # F scales perfectly into a clean inner product variant:
    F = p**2 + p * (Ta * Tb.conjugate() + 1).real + 1.0
    
    if abs(F) < 1e-12:
        raise ValueError("Parameter p matches a discontinuous biarc boundary.")
    
    # Elegant complex projection mapping the poles A(-1) and B(1) to J
    J = ((p**2 - 1.0) + 1j * p * (Ta - Tb)) / F

    # --- 2. Compute the Tangent Phasor at the Junction (Tj) ---
    # Using complex square roots avoids half-angle tan arithmetic entirely
    num = p * cmath.sqrt(Ta) + cmath.sqrt(Tb)
    
    # Squaring the normalized numerator naturally recovers the full exit tangent
    Tj = -(num / abs(num))**2
    
    # --- 3. Compute Arc Heading Changes (theta1, theta2) ---
    # Relative rotations are just the phase angles of the phasor quotients
    theta1 = cmath.phase(Tj / Ta)
    theta2 = cmath.phase(Tb / Tj)
    
    return {
        "junction": J,
        "tangent_at_junction": Tj,       # Returned as a complex unit vector
        "arc1_heading_change": theta1,    # In radians, naturally in (-pi, pi]
        "arc2_heading_change": theta2     # In radians, naturally in (-pi, pi]
    }


def compute_biarc_original_hybrid(p1, t1, p2, t2):
    p1 = np.array(p1, dtype=float)
    p2 = np.array(p2, dtype=float)
    t1 = np.array(t1, dtype=float) / np.linalg.norm(t1)
    t2 = np.array(t2, dtype=float) / np.linalg.norm(t2)
    
    v = p2 - p1
    v_dot_t1 = np.dot(v, t1)
    v_dot_t2 = np.dot(v, t2)
    t1_dot_t2 = np.dot(t1, t2)
    
    # 1. Revert to the original symmetric weight formula
    a = 2.0 * (1.0 - t1_dot_t2)
    b = 2.0 * (v_dot_t1 + v_dot_t2)
    c = -np.dot(v, v)
    
    discriminant = b**2 - 4*a*c
    d1 = (-b + np.sqrt(discriminant)) / (2.0 * a)
    d2 = d1

    # Exact original formula for the junction point
    pm = p1 + d1 * t1 + (p2 - p1 - d1*t1 - d2*t2) / 2.0 
    
    def find_arc_center_radius(p_start, t_start, p_end):
        # Center is intersection of tangent normal and chord perpendicular bisector
        n_start = np.array([-t_start[1], t_start[0]])
        mid = (p_start + p_end) / 2.0
        chord = p_end - p_start
        n_chord = np.array([-chord[1], chord[0]])
        
        A = np.column_stack((n_start, -n_chord))
        B = mid - p_start
        alpha, beta = np.linalg.solve(A, B)
        
        center = p_start + alpha * n_start
        radius = np.linalg.norm(p_start - center)
        return center, radius

    # 2. Independently compute Arc 1 and Arc 2 properties from Pm
    c1, r1 = find_arc_center_radius(p1, t1, pm)
    c2, r2 = find_arc_center_radius(p2, -t2, pm) # Path arriving at P2 along t2
    
    # Calculate the continuous joint tangent at Pm
    v_pm = pm - c1
    cross = (p1 - c1)[0]*t1[1] - (p1 - c1)[1]*t1[0]
    tm = np.array([-v_pm[1], v_pm[0]]) if cross > 0 else np.array([v_pm[1], -v_pm[0]])
    tm = tm / np.linalg.norm(tm)
    
    return p1, pm, p2, c1, r1, c2, r2, t1, t2, tm

def get_arc_points(center, p_start, p_end, t_start, num_points=100):
    v_start = p_start - center
    v_end = p_end - center
    r = np.linalg.norm(v_start)
    
    ang_start = np.arctan2(v_start[1], v_start[0])
    ang_end = np.arctan2(v_end[1], v_end[0])
    
    # Check rotation orientation via cross product
    cross_prod = v_start[0] * t_start[1] - v_start[1] * t_start[0]
    is_ccw = cross_prod > 0
    
    if is_ccw:
        if ang_end <= ang_start:
            ang_end += 2 * np.pi
    else:
        if ang_end >= ang_start:
            ang_end -= 2 * np.pi
            
    angles = np.linspace(ang_start, ang_end, num_points)
    return center[0] + r * np.cos(angles), center[1] + r * np.sin(angles)

def find_locus_circle(p1, pm, p2):
    """Computes the circle passing through the three points P1, Pm, and P2."""
    mid12 = (p1 + p2) / 2.0
    v12 = p2 - p1
    n12 = np.array([-v12[1], v12[0]])
    
    midm2 = (pm + p2) / 2.0
    vm2 = p2 - pm
    nm2 = np.array([-vm2[1], vm2[0]])
    
    A = np.column_stack((n12, -nm2))
    B = midm2 - mid12
    res = np.linalg.solve(A, B)
    
    center = mid12 + res[0] * n12
    radius = np.linalg.norm(p1 - center)
    return center, radius

# --- Run & Plot ---
p1_in, t1_in = [0.0, 0.0], [1.0, 1.0]
p2_in, t2_in = [4.0, 1.0], [1.0, -1.0]
p1_in, t1_in = [0.0, 0.0], [-1, -1.0]
p2_in, t2_in = [4.0, 1.0], [1.0, -1.0]

p1, pm, p2, c1, r1, c2, r2, t1, t2, tm = compute_biarc_original_hybrid(p1_in, t1_in, p2_in, t2_in)
c_locus, r_locus = find_locus_circle(p1, pm, p2)

x1, y1 = get_arc_points(c1, p1, pm, t1)
x2, y2 = get_arc_points(c2, pm, p2, tm)

# Complete locus circle sweep
angles = np.linspace(0, 2 * np.pi, 200)
x_locus = c_locus[0] + r_locus * np.cos(angles)
y_locus = c_locus[1] + r_locus * np.sin(angles)

# Plotting
plt.figure(figsize=(10, 6))

plt.scatter([p1[0], pm[0], p2[0]], [p1[1], pm[1], p2[1]], color='black', zorder=5)
plt.text(p1[0], p1[1]-0.2, ' P1', fontdict={'weight': 'bold'})
plt.text(pm[0], pm[1]+0.1, ' Pm (Junction)', fontdict={'weight': 'bold', 'color': 'purple'})
plt.text(p2[0], p2[1]-0.2, ' P2', fontdict={'weight': 'bold'})

# Render tangent vectors
plt.quiver(*p1, *t1, color='blue', scale=6, zorder=4, label='T1')
plt.quiver(*p2, *t2, color='red', scale=6, zorder=4, label='T2')
plt.quiver(*pm, *tm, color='purple', scale=6, zorder=4, label='Tm')

plt.axis('equal')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(loc='upper left')
xl=plt.xlim()
yl=plt.ylim()

plt.plot(x_locus, y_locus, 'g--', alpha=0.4, label='Junction Locus Circle')
plt.plot(x1, y1, 'b-', linewidth=2.5, label='Arc 1 (P1 to Pm)')
plt.plot(x2, y2, 'r-', linewidth=2.5, label='Arc 2 (Pm to P2)')
plt.xlim(xl)
plt.ylim(yl)
plt.gca().set_aspect('equal')
plt.title("Accurate G1 Biarc connection with Junction Locus Circle")
plt.show()
