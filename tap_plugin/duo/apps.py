"""TAP Duo plugin AppConfig — the base ready() registers the manifest; this one adds the plugin's
own panel type, the posture strip (req-duo-panel-posture)."""

from tap_plugins.base import TapPluginConfig


class DuoConfig(TapPluginConfig):
    def ready(self) -> None:
        super().ready()
        from tap_plugin.duo.panels.duo_posture import DuoPosturePanelType

        from tap_web.registry import panel_type_registry

        panel_type_registry.register(DuoPosturePanelType.slug, DuoPosturePanelType)
