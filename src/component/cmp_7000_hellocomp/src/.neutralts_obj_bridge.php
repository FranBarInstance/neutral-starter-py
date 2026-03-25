<?php
header('Content-Type: application/json');
$raw = file_get_contents('php://input');
$payload = json_decode($raw, true);

if (!is_array($payload)) {
    echo json_encode(["__neutralts_obj_error" => "invalid payload"]);
    exit;
}

$script_file = $payload["script_file"] ?? "";
$callback = $payload["callback"] ?? "main";
$params = $payload["params"] ?? [];
$GLOBALS["__NEUTRAL_SCHEMA__"] = $payload["schema"] ?? null;
$GLOBALS["__NEUTRAL_SCHEMA_DATA__"] = $payload["schema_data"] ?? null;
$GLOBALS["__NEUTRAL_VENV__"] = $payload["venv"] ?? null;

if (!is_string($script_file) || $script_file === "" || !is_file($script_file)) {
    echo json_encode(["__neutralts_obj_error" => "obj script not found"]);
    exit;
}

try {
    require_once $script_file;
} catch (Throwable $e) {
    echo json_encode(["__neutralts_obj_error" => "php script load failed"]);
    exit;
}

if (!is_callable($callback)) {
    echo json_encode(["__neutralts_obj_error" => "callback not found"]);
    exit;
}

try {
    $result = call_user_func($callback, $params);
} catch (Throwable $e) {
    echo json_encode(["__neutralts_obj_error" => "callback execution failed"]);
    exit;
}

$json = json_encode($result);
if ($json === false) {
    echo json_encode(["__neutralts_obj_error" => "invalid callback response"]);
    exit;
}

echo $json;
