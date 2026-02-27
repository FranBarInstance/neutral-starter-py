<?php
function main($params = []) {
    $schema = $GLOBALS['__NEUTRAL_SCHEMA__'] ?? null;
    $schema_data = $GLOBALS['__NEUTRAL_SCHEMA_DATA__'] ?? null;

    return [
        "data" => [
            "message" => "I'm a message from a component in obj"
        ],
    ];
}
