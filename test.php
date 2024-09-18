function get_airtable_events() {

    $api_url = 'https://api.airtable.com/v0/app7g2ANnagHYZkZ8/tbleWW3ENwjP0uDgh';

    // Заголовки для авторизации и формата запроса
    $headers = array(
        'Authorization' => 'Bearer patH7vMYiTOyuJqrZ.07c6baf72a40d99653c1ea516814884ba6a34421672d138377236a6186dda389', // Используй свой API-ключ
        'Content-Type'  => 'application/json'
    );

    // Выполнение запроса к API Airtable
    $response = wp_remote_get($api_url, array(
        'headers' => $headers
    ));

    // Проверка на ошибки
    if (is_wp_error($response)) {
        return 'Ошибка при выполнении запроса: ' . $response->get_error_message();
    }

    // Получение тела ответа
    $body = wp_remote_retrieve_body($response);

    // Преобразование JSON ответа в массив PHP
    $data = json_decode($body, true);

    return $data['records'];
}

function display_events_calendar() {
    $events = get_airtable_events();

    if (empty($events)) {
        echo "Нет событий для отображения.";
        return;
    }

    foreach ($events as $event) {
        $fields = $event['fields'];
        echo "<div class='event'>";
        echo "<h3>{$fields['Название события']}</h3>";
        echo "<p>Дата: {$fields['Дата']}</p>";
        echo "<p>Свободных мест: {$fields['Количество мест']}</p>";
        echo "</div>";
    }
}

add_shortcode('airtable_events', 'display_events_calendar');
