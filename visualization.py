# This script uses the variants aggregated with timing and sofa information generated by main.py and
# provides a visualization
import pickle
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import math
#Use the comorbitities that you would like to control for, you should have calculated the results first using main.py
comorbs_list = [["congestive_heart_failure","myocardial_infarct","chronic_pulmonary_disease"]]#[["renal_disease"]]#[["malignant_cancer","metastatic_solid_tumor "]]#[["diabetes_without_cc","diabetes_with_cc"]]#[["age_score"]]#[["congestive_heart_failure","myocardial_infarct","chronic_pulmonary_disease"]]#[["age_score"]]#["renal_disease"],["mild_liver_disease","severe_liver_disease"],["congestive_heart_failure","myocardial_infarct","chronic_pulmonary_disease"],["malignant_cancer","malignant_cancer"]]
for comorbs in comorbs_list:
    res = {}
    res_outcome = {}
    variants = {}
    controls = {}
    frequencies = {}
    with open('result'+comorbs[0]+'.pkl', 'rb') as f:
        res = pickle.load(f)

    with open('result_outcome'+comorbs[0]+'.pkl', 'rb') as f:
        res_outcome = pickle.load(f)

    with open('variants'+comorbs[0]+'.pkl', 'rb') as f:
        variants = pickle.load(f)

    with open('frequency'+comorbs[0]+'.pkl', 'rb') as f:
        frequencies = pickle.load(f)

    colors = {"VENTILATION": "#003f5c","PRESSOR":"#bc5090", "DIALYSIS":"#ffa600","ADMIT":"#111111","DISCHARGE":"#eeeeee" }
    plt.rcParams["figure.figsize"] = (16, 12)
    total_number = sum([len(variants[var]) for var in variants.keys()])
    for c in res.keys():
        for var in res[c].keys():
            #print(variants[var][0][2])
            var_arr = variants[var][0][2]
            lines = []
            for l in var_arr:
                start = None
                end = None
                act = None
                for x in range(0,len(l)):
                    if l[x] != 'None':
                        if start == None:
                            start = x
                            act = l[x]
                        else:
                            end = x
                lines.append((act,start,end))

            for i in range(0,len(lines)):
                (act, start, end) = lines[i]
                y = lines.index((act, start, end))
                x_list = [j for j in range(start, end+1)]
                y_list = [y for _ in x_list]

                if act != "ADMIT" and act != "DISCHARGE":
                    plt.plot(x_list, y_list, color=colors[act], label=act, linewidth=30, solid_capstyle='butt')
                    plt.text(x_list[0]+0.1, y-0.08,act, fontsize = 14, color = "white", fontweight = 700)
                else:
                    plt.plot(x_list,y_list, color=colors[act], label=act, linewidth=30, solid_capstyle='butt')
            plt.ylim(-0.5, len(lines)+0.5)
            groups = sorted(list(res[c][var].keys()))
            #print(groups)
            groups = [x for x in groups if x not in ['OTHER',  'UNKNOWN', 'UNABLE TO OBTAIN', 'AMERICAN INDIAN/ALASKA NATIVE']]
            color_list = ["#063852","#c4bc8c","#984756","#fcc46c","#fbb34c","#4b2c44"]
            c_map = {}
            for j in range(0,len(groups)):
                c_map[groups[j]] = color_list[j%6]
            diffs = [ (i,i+1) for i in range(0,len(var_arr[0])-1)]
            #diffs = [[(i,i+j) for j in range(1,len(var_arr[0])-i)]for i in range(0,len(var_arr[0])-1)]
            #diffs = list(chain.from_iterable(diffs))
            diffs += [(lines[i][1], lines[i][2])for i in range(0,len(lines))]
            #print(diffs)
            #print(lines)
            height_dict= {}
            event_dict = {}
            event_act_dict= {}
            for (s, e) in diffs:
                # find height
                height = -1
                skip = False
                event = False
                event_act = ""
                for i in range(0, len(lines)):
                    (act, start, end) = lines[i]
                    if start == s and end == e:
                        height = i+0.1
                        event = True
                        event_act = act
                    elif start == e:
                        height = i
                    elif end == s:
                        height = i
                if height == -1:
                    continue
                height_dict[(s,e)] = height
                event_dict[(s, e)] = event
                event_act_dict[(s,e)] = event_act
                if not event:
                    plt.plot([s, e], [height, height], color="black")
                    plt.plot([s], [height], marker="o" ,color="black")
                    plt.plot([e], [height], marker=">", color="black", linewidth= 5)
            #print(height_dict)
            max_x = max([end for (act, start, end) in lines] )
            max_x = 1
            first_class = True
            first_group = ""
            for k in groups:
                #print(res[c][var][k].keys())
                if first_class:
                    first_group = k
                    first_class = False
                for (s,e) in res[c][var][k].keys():
                    (v_low, v_high) = res[c][var][k][(s, e)][0]
                    (sofa_v_low, sofa_v_high) = res[c][var][k][(s, e)][1]
                    # can be added if hypothesis test is conducted
                    #(v,p) = res[c][var][k][(s,e)] old with p
                    if (s,e) not in height_dict.keys():
                        continue
                    #can be added if hypothesis test is conducted
                    p_s = "" #if p > 0.01 else "*"
                    v_s_mid = (v_low + v_high)/2
                    v_dev = v_high - v_s_mid
                    v_s = str(int(v_s_mid/3600))+""+"±"+str(int(v_dev/3600))+"h"
                    #v_s = str(int(v_low/3600))+"h"+", "+str(int(v_high/3600))+"h"
                    sofa_s_mid = (sofa_v_low + sofa_v_high) / 2
                    sofa_s_dev = sofa_v_high - sofa_s_mid
                    sofa_s = str(round(sofa_s_mid, 1)) + "±" + str(round(sofa_s_dev, 1))
                    #sofa_s = str(round(sofa_v_low,1))+", "+ str(round(sofa_v_high,1))#if not math.isnan(sofa_v) else -1
                    if event_dict[(s,e)]:
                        # This could be used to display * when conducting hypothesis testing for each difference
                        # if event_act_dict[(s,e)] != "ADMIT" and event_act_dict[(s,e)] != "DISCHARGE":
                        #     plt.text(x = s+ 0.5+ groups.index(k)*0.3*max_x, y= height_dict[(s,e)]+0.05*len(lines), s=v_s+p_s, color = c_map[k], fontsize = 14, fontweight = 600 )
                        #     if k == first_group:
                        #         plt.text(x=s + 0.05 + groups.index(k) * 0.1 * max_x,
                        #                  y=height_dict[(s, e)] + 0.05 * len(lines),
                        #                  s="TIME: " + p_s, color=c_map[k], fontsize=14, fontweight=600)
                        # if k == first_group:
                        #     plt.text(x=s + 0.05 + 0 * 0.1 * max_x, y=height_dict[(s, e)] + 0.1 * len(lines),
                        #              s="SOFA: ", color=c_map[k], fontsize=14, fontweight=600)
                        #     #plt.text(x=s + 0.05 + groups.index(k) * 0.1 * max_x, y=height_dict[(s, e)] + 0.05 * len(lines),
                        #     #         s="TIME: " + p_s, color=c_map[k], fontsize=14, fontweight=600)
                        #     first_class = False
                        # plt.text(x=s + 0.5 + groups.index(k) * 0.3 * max_x, y=height_dict[(s, e)] + 0.1 * len(lines),
                        #      s=sofa_s, color=c_map[k], fontsize=14, fontweight=600)
                        if event_act_dict[(s,e)] != "ADMIT" and event_act_dict[(s,e)] != "DISCHARGE":
                            plt.text(x = e-0.4, y= height_dict[(s,e)] + 0.05+ groups.index(k)*0.16, s=v_s+p_s, color = c_map[k], fontsize = 14, fontweight = 600 )
                            if k == first_group:
                                plt.text(x = e-0.4, y= height_dict[(s,e)] + 0.05+ len(groups)*0.16,
                                         s="TIME" + p_s, color=c_map[k], fontsize=14, fontweight=600)
                        if k == first_group:
                            plt.text(x = s, y= height_dict[(s,e)] + 0.05+ len(groups)*0.16,
                                     s="SOFA", color=c_map[k], fontsize=14, fontweight=600)
                            #plt.text(x=s + 0.05 + groups.index(k) * 0.1 * max_x, y=height_dict[(s, e)] + 0.05 * len(lines),
                            #         s="TIME: " + p_s, color=c_map[k], fontsize=14, fontweight=600)
                            first_class = False
                        plt.text(x = s, y= height_dict[(s,e)] + 0.05+ groups.index(k)*0.16,
                             s=sofa_s, color=c_map[k], fontsize=14, fontweight=600)
                    else:
                        plt.text(x = s+0.2, y= height_dict[(s,e)] + 0.1+ groups.index(k)*0.16, s=v_s+p_s, color = c_map[k], fontsize = 14, fontweight = 600 )
                    #print(v,p) old
                    #print(v_low)
            plt.axis("off")
            #get frequencies of classes
            freq_sum = sum([frequencies[c][var][k_v] for k_v in frequencies[c][var].keys()])
            freq_dict = {k_v: frequencies[c][var][k_v]/freq_sum for k_v in frequencies[c][var].keys()}
            legend1 = plt.legend(loc = "upper left",handles=[mpatches.Patch(color=c_map[g], label=g+" ("+"{0:.0%}".format(freq_dict[g])+")") for g in reversed(groups)],fontsize=16)
            plt.gca().add_artist(legend1)
            # Add the outcome legend
            outcome = "LOS"
            patches = []
            for g in reversed(groups):
                out_mid = (res_outcome[c][var][g][outcome][0] + res_outcome[c][var][g][outcome][1])/2
                out_dev = res_outcome[c][var][g][outcome][1] - out_mid
                patches.append(mpatches.Patch(color=c_map[g], label=g + " " + "{0:.1f}".format(out_mid) + "±" + "{0:.1f}d".format(out_dev)))
            legend2 = plt.legend(loc="upper right", handles=patches, fontsize=16, title=outcome)

            legend2.get_title().set_fontsize("16")
            plt.gca().add_artist(legend2)

            outcome = "Mortality"
            patches = []
            for g in reversed(groups):
                out_mid = (res_outcome[c][var][g][outcome][0] + res_outcome[c][var][g][outcome][1]) / 2
                out_dev = res_outcome[c][var][g][outcome][1] - out_mid
                patches.append(mpatches.Patch(color=c_map[g],
                                              label=g + " " + "{0:.1%}".format(out_mid) + "±" + "{0:.1%}".format(
                                                  out_dev)))
            legend2 = plt.legend(loc="lower right", handles=patches, fontsize=16, title=outcome)

            legend2.get_title().set_fontsize("16")
            plt.gca().add_artist(legend2)


            plt.title("Time lags for variant with " + str(len(variants[var])) +" patients (" + str(int((len(variants[var]) / total_number) * 10000) / 100) + "%)",fontsize=20)
            #plt.tight_layout()
            #plt.show()

            plt.savefig("results/"+c+"/"+var.replace("None","N")+".png", dpi = 600)
            plt.show()


    # for c in controls.keys():
    #     cv_dfs = {}
    #     for cv in controls[c][list(controls[c].keys())[0]].keys():
    #         cv_dfs[cv] = {}
    #         for k in controls[c].keys():
    #             if k in ['OTHER',  'UNKNOWN', 'UNABLE TO OBTAIN', 'AMERICAN INDIAN/ALASKA NATIVE']:
    #                 continue
    #             cv_dfs[cv][k] = controls[c][k][cv]
    #
    #     for cv in cv_dfs.keys():
    #         ax = pd.DataFrame(cv_dfs[cv]).plot.bar()
    #         ax.spines.right.set_visible(False)
    #         ax.spines.top.set_visible(False)
    #         ax.set_title(cv+" for "+c)
    #         ax.set_xlabel(cv)
    #         ax.set_ylabel("Relative frequency")
    #         plt.tight_layout()
    #         plt.savefig(c + "_new_filter/" + cv + ".png", dpi=600)
    #         #plt.show()
    #
    #     #cv_df.plot.bar(x=c)

