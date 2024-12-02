from fasthtml.common import *

app, rt = fast_app(debug=True)

db = database("proyectoCarro.db") 
autos = db.t.auto

if autos not in db.t:
    autos.create(idAuto=int, placa=str, modelo=str, marca=str, año=int, disponibilidad=str, pk='idAuto')

Auto = autos.dataclass()

def create_form():
    return Form(id="create-form", hx_post="/", hx_target="#auto-list", hx_swap="beforeend")

def create_row():
    return Tr(
        Th("Agregar"),
        Th(Input(name="placa", type="text", placeholder="Placa", form="create-form")),
        Th(Input(name="modelo", type="text", placeholder="Modelo", form="create-form")),
        Th(Input(name="marca", type="text", placeholder="Marca", form="create-form")),
        Th(Input(name="año", type="number", placeholder="Año", form="create-form")),
        Th(Input(name="disponibilidad", type="text", placeholder="Disponibilidad", form="create-form")),
        Th(Input(type="submit", value="Agregar", form="create-form")),
        id="create-row", hx_swap_oob="true"
    )

def auto_cell(auto_id: int, column_name: str, column_value: str, edit: bool = False):
    cell_id = f"auto-{auto_id}-{column_name}"
    attributes = {
        "id": cell_id,
        "hx_swap": "outerHTML",
        "hx_vals": {'pre_value': column_value},
    }
    if edit:
        inner_html = Input(name=column_name,
                            value=column_value,
                            type="text" if column_name != "año" else "number",
                            hx_post=f"/update/{auto_id}/{column_name}",
                            target_id=cell_id,
                            hx_swap="outerHTML",
                            hx_trigger="keyup[key=='Enter'] changed",
                        )
        attributes["hx_trigger"] = "keyup[key=='Escape']"
        attributes["hx_post"] = f"/reset/{auto_id}/{column_name}"
    else:
        inner_html = column_value
        attributes["hx_trigger"] = "click"
        attributes["hx_post"] = f"/swap/{auto_id}/{column_name}"
    return Td(inner_html, **attributes)

def auto_row(auto: Auto):
    return Tr(
        Td(auto.idAuto),
        auto_cell(auto.idAuto, "placa", auto.placa),
        auto_cell(auto.idAuto, "modelo", auto.modelo),
        auto_cell(auto.idAuto, "marca", auto.marca),
        auto_cell(auto.idAuto, "año", str(auto.año)),
        auto_cell(auto.idAuto, "disponibilidad", auto.disponibilidad),
        Td(
            Button("Eliminar",
                    hx_delete=f"/{auto.idAuto}",
                    hx_confirm="Estas Seguro?",
                    hx_swap="outerHTML",
                    target_id=f"auto-{auto.idAuto}"
                    ),
        ),
        id=f"auto-{auto.idAuto}"
    )

def auto_table():
    return Table(
        Thead(
            Tr(
                Th("ID", scope="col"),
                Th("Placa", scope="col"),
                Th("Modelo", scope="col"),
                Th("Marca", scope="col"),
                Th("Año", scope="col"),
                Th("Disponibilidad", scope="col"),
                Th("Acción", scope="col")
            ),
            create_row()
        ),
        Tbody(
            map(auto_row, autos()), id="auto-list"
        )
    )

@rt("/")
def get():
    return Titled("Autos", create_form(), auto_table())

@rt("/")
def post(auto: Auto):
    new_auto = autos.insert(auto)
    return auto_row(new_auto), create_row()

@rt("/swap/{auto_id:int}/{column_name:str}")
def post(auto_id: int, column_name: str, pre_value: str):
    return auto_cell(auto_id, column_name, pre_value, edit=True)

@rt("/update/{auto_id:int}/{column_name:str}")
def post(auto_id: int, column_name: str, auto: Auto):
    auto.idAuto = auto_id
    auto = autos.update(auto)
    return auto_cell(auto_id, column_name, getattr(auto, column_name))

@rt("/reset/{auto_id:int}/{column_name:str}")
def post(auto_id: int, column_name: str, pre_value: str):
    return auto_cell(auto_id, column_name, pre_value)

@rt("/{auto_id:int}")
def delete(auto_id: int):
    autos.delete(auto_id)
    return

serve()