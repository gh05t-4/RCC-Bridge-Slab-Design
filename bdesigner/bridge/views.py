from math import pi, sqrt

from django.shortcuts import render

from .forms import Dimensions


def designer(carriage_way, foot_path, span, bearing_width, wear_coat):
    results_dict = {}

    fck = 25
    fy = 415
    Es= 200
    Ec = 30
    alpha_e = round((Es / Ec), 2)
    K_dict = {
        0.1: 0.4,
        0.2: 0.8,
        0.3: 1.16,
        0.4: 1.48,
        0.5: 1.72,
        0.6: 1.96,
        0.7: 2.12,
        0.8: 2.24,
        0.9: 2.36,
        1.0: 2.48,
        1.1: 2.6,
        1.2: 2.64,
        1.3: 2.72,
        1.4: 2.8,
        1.5: 2.84,
        1.6: 2.88,
        1.7: 2.92,
        1.8: 2.96,
    }

    # Depth of slab and effective span
    d1 = (span * 10**3) / 15
    d2 = (span * 10**3) / 12
    d3 = (80 * 6)

    d = max(d1, d2, d3)

    eff_d = d - 40 - 10 # clear cover = 40mm, dia of the bar = 20mm

    eff_span = min((span + (eff_d / 10**3)), (span + (bearing_width / 10**3)))

    results_dict.update({"depth": round(d, 2), "eff_d": round(eff_d, 2), "eff_span": eff_span})

    # Dead Load bending moments
    dead_wt_slab = (d / 10**3) * 24
    dead_wt_wc = (wear_coat / 10**3) * 22
    total_load = round(dead_wt_slab + dead_wt_wc, 0)
    dead_load_bm = round((total_load * eff_span**2) / 8, 2)
    # print(dead_load_bm)
    results_dict.update({"total_dead_load": total_load, "dead_load_bm": dead_load_bm})

    # Live load bending moments
    impact_factor = 25 - (15 / 4) * (eff_span - 5)
    eff_len_load = 3.6 + 2 * (d / 10**3 + wear_coat / 10**3)

    x1 = eff_span / 2

    B = carriage_way + 2 * foot_path

    B_by_L = round(B / eff_span, 1)

    if B_by_L >= 1.9:
        K = 3
    else:
        K = K_dict[B_by_L]

    b_w = 0.85 + (2 * wear_coat / 10**3)

    b_e1 = round(K * x1 * (1 - x1 / eff_span) + b_w, 2)

    net_eff_w_dispersion = foot_path * 10**3 + 1200 + 850 + 1200 + 850 / 2 + (b_e1 * 10**3 / 2)

    total_load_2_track_impact = 700 * 1.197

    avg_load_intensity1 = total_load_2_track_impact / (4.76 * net_eff_w_dispersion / 10**3)

    M_max = round((0.5 * (avg_load_intensity1 * 4.76) * x1) - (0.5 * (avg_load_intensity1 * 4.76) * (4.76 * 0.25)), 0)
    # print(M_max)

    total_design_bm = M_max + dead_load_bm

    M_u = round((1.35 * dead_load_bm) + (1.5 * M_max), 2)

    # print(total_design_bm)
    # print(M_u)
    results_dict.update({"ll_max_M": M_max, "ll_total_design_bm": total_design_bm, "ultimate_M": M_u})

    # shear due to class AA tracked vehicle
    x2 = 4.76 / 2

    b_e2 = round(K * x2 * (1 - x2 / eff_span) + b_w, 3)
    disp_width = foot_path * 10**3 + 1200 + 850 + 1200 + 850 / 2 + (0.5 * b_e2 * 10**3)
    avg_load_intensity2 = total_load_2_track_impact / (4.76 * disp_width / 10**3)
    V_a = round(avg_load_intensity2 * 4.76 * round((eff_span - x2), 2) / eff_span, 0)
    dead_load_shear = 0.5 * total_load * eff_span

    total_design_shear = round(V_a + dead_load_shear, 1)
    V_u = round(1.35 * dead_load_shear + 1.5 * V_a, 2)

    # print(total_design_shear, V_u)
    results_dict.update({"shear_force": V_a, "total_design_shear": total_design_shear, "ultimate_shear": V_u})

    # Design of deck slab
    b = 1000
    d0 = sqrt(M_u * 10**6 / (0.138 * fck * b))

    if d0 < eff_d:
        co1 = fy**2 * 0.87 / (b * fck)
        co2 = -0.87 * fy * eff_d
        co3 = M_u * 10**6

        Ast1 = (-co2 + sqrt(co2**2 - (4 * co1 * co3))) / (2 * co1)
        Ast2 = (-co2 - sqrt(co2**2 - (4 * co1 * co3))) / (2 * co1)

        Ast = round(min(Ast1, Ast2), 2)
    else:
        print("Over reinforced.")

    # print(Ast)
    ast = pi * 20**2 / 4

    S = (1000 * ast) / Ast

    if S % 50 != 0:
        S = S - S % 50
        Ast_provided = round((1000 * ast) / S, 2)
    else:
        Ast_provided = Ast

    results_dict.update({"main_st_dia": 20, "Ast_provided": Ast_provided, "main_st_S": S})

    # print(S, Ast_provided)

    transverse_moment = round(0.3 * (1.5 * M_max) + 0.2 * (1.35 * dead_load_bm), 2)
    area_dist_reinf = round((Ast_provided / M_u) * transverse_moment, 0)

    t_S = (pi * 12**2 * 1000) / (4 * area_dist_reinf)

    if t_S % 50 != 0:
        t_S -= t_S % 50

    # print(t_S)
    results_dict.update({"transv_M": transverse_moment, "dia_st": 12, "area_rein": area_dist_reinf, "transv_S": t_S})

    # Check for Ultimate Flexural Strength
    M_u_check = (0.87 * fy * Ast_provided * eff_d) * (1 - (Ast_provided * fy / (b * eff_d * fck)))
    M_u_check = round(M_u_check / 10**6, 2)

    if M_u_check > M_u:
        flex_strength = "Safe"
        # print(M_u_check, M_u)
    else:
        flex_strength = "Not safe"

    # Check for Ultimate Shear Strength
    K = 1 + sqrt(200 / eff_d)
    if K > 2:
        K = 2

    rho1 = (Ast_provided / (b *eff_d))
    if rho1 > 0.02:
        rho1 = 0.02

    V_Rd_c = round((0.12 * K * (80 * rho1 * fck)**0.33) * b * eff_d / 1000, 0)

    if V_Rd_c > V_u:
        shear_strength = "Safe"
    else:
        shear_strength = "Not safe"

    results_dict.update({"flex_check": flex_strength, "shear_check": shear_strength})

    return results_dict

# Create your views here.
def index(request):
    if request.method == "POST":
        form = Dimensions(request.POST)
        if form.is_valid():
            carriage_way = request.POST['carriage_way']
            foot_path = request.POST['foot_path']
            span = request.POST['span']
            bearing_width = request.POST['bearing_width']
            wear_coat = request.POST['wear_coat']
            
            if carriage_way.replace('.', '').isdigit() and foot_path.replace('.', '').isdigit() and span.isdigit() and bearing_width.isdigit() and wear_coat.isdigit():
                design_params = designer(float(carriage_way), float(foot_path), int(span), int(bearing_width), int(wear_coat))
            else:
                design_params = {"invalid_input": "Only numbers are valid."}

            context = design_params
            return render(request, "bridge/results.html", context)
    else:
        form = Dimensions()

    return render(request, "bridge/index.html", {'form': form})