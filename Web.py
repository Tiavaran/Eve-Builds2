from flask import Flask, render_template
import Evebuilds
#from Evebuilds import pitl, calculatepercentages, esi_get_name, get_count
app = Flask(__name__)


@app.route('/')
def index():
    H_items = Evebuilds.pstl()
    H_names = Evebuilds.check_cache(H_items)
    return render_template("HomePage.html",H_items=H_items, H_names=H_names)

@app.route('/<hull_id>')
def hullpage(hull_id):
    mlist = [hull_id]
    hull_name = Evebuilds.check_cache(mlist)

    H_Ilist = Evebuilds.pitl(hull_id, 0)
    H_Plist = Evebuilds.calculatepercentages(hull_id, 0)
    H_names = Evebuilds.check_cache(H_Ilist)
    h_count = Evebuilds.get_count(hull_id, 0)

    M_Ilist = Evebuilds.pitl(hull_id, 1)
    M_Plist = Evebuilds.calculatepercentages(hull_id, 1)
    M_names = Evebuilds.check_cache(M_Ilist)
    M_count = Evebuilds.get_count(hull_id, 1)

    L_Ilist = Evebuilds.pitl(hull_id, 2)
    L_Plist = Evebuilds.calculatepercentages(hull_id, 2)
    L_names = Evebuilds.check_cache(L_Ilist)
    L_count = Evebuilds.get_count(hull_id, 2)

    R_Ilist = Evebuilds.pitl(hull_id, 3)
    R_Plist = Evebuilds.calculatepercentages(hull_id, 3)
    R_names = Evebuilds.check_cache(R_Ilist)
    R_count = Evebuilds.get_count(hull_id, 3)
    return render_template("HullTemp.html", hull_id=hull_id, hull_name=hull_name, H_items=H_Ilist, H_names=H_names, H_percent=H_Plist, HCount=h_count, M_items=M_Ilist, M_names=M_names, M_percent=M_Plist, MCount=M_count, L_items=L_Ilist,L_names=L_names, L_percent=L_Plist,LCount=L_count,R_items=R_Ilist, R_names=R_names, R_percent=R_Plist,RCount=R_count)

if __name__ == "__main__":
    app.run(debug=True)
