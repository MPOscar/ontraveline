function split_columns(){


    // 1 - Obtener el Texto a visualizar en la página
    var descripcion_destino = $('p.descripcion_destino');
    var descripcion_destino_text = descripcion_destino.text();

    // 2 - Dividirlo en dos columnas de número aproximadamente igual de caracteres
    // 2.1 - Dividir el texto en dos grupos de caracteres lo más iguales posibles
    // 2.2 - Separar
    var caracteres_texto = descripcion_destino_text.length;
    var caracteres_columna_1 = parseInt(caracteres_texto / 2);

    var column_1 = descripcion_destino_text.slice(1, caracteres_columna_1);
    var column_2 = descripcion_destino_text.slice(caracteres_columna_1, caracteres_texto);

    while (column_2[0] != " ") {
        c = column_2.slice(0, 1);
        column_1 += c;
        column_2 = column_2.slice(1, column_2.length);
    }

    var columna_1 = $('td.first');
    var columna_2 = $('td.second');

    columna_1.html(column_1);
    columna_2.html(column_2);

    descripcion_destino.hide();

    // var destino_id = descripcion_destino.getAttribute('id');
    // alert(destino_id);
}

$(document).ready(
   split_columns
);