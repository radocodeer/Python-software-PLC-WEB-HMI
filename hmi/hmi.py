from dearpygui import dearpygui as dpg
import threading
import time


class PLCState:
    STOP = "STOP"
    START = "START"
    RUN = "RUN"
    FAULT = "FAULT"


class PLC_HMI:

    def __init__(self, plc):
        self.plc = plc

        dpg.create_context()

        # =========================
        # MODERN 2026 INDUSTRIAL THEME
        # =========================
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):

                # background
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (10, 12, 18))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (16, 18, 26))
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (20, 22, 30))

                # frames / cards
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (26, 30, 42))
                dpg.add_theme_color(dpg.mvThemeCol_Border, (45, 55, 75))

                # buttons (neon industrial)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 170, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 210, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 120, 190))

                # text
                dpg.add_theme_color(dpg.mvThemeCol_Text, (220, 235, 255))

                # style
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 12)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 6)

        dpg.bind_theme(global_theme)

        # =========================
        # VIEWPORT
        # =========================
        dpg.create_viewport(
            title="Virtual PLC HMI 2026",
            width=1100,
            height=650
        )

        # =========================
        # WINDOW 1: PLC STATUS PANEL
        # =========================
        with dpg.window(label="PLC CONTROL CENTER",
                        width=400, height=200, pos=(10, 10)):

            dpg.add_text("PLC STATUS", color=(0, 200, 255))

            self.state_text = dpg.add_text(
                self.plc.state,
                color=(0, 255, 140)
            )

            dpg.add_separator()

            with dpg.group(horizontal=True):

                dpg.add_button(label="START", width=110, callback=self.start_plc)
                dpg.add_button(label="STOP", width=110, callback=self.stop_plc)
                dpg.add_button(label="FAULT", width=110, callback=self.fault_plc)

            dpg.add_separator()

            self.log_text = dpg.add_text("System ready...")

        # =========================
        # WINDOW 2: HMI PANEL
        # =========================
        with dpg.window(label="INDUSTRIAL HMI",
                        width=650, height=600, pos=(420, 10)):

            dpg.add_text("MOTOR CONTROL SYSTEM", color=(0, 200, 255))
            dpg.add_text("Real-time PLC I/O Monitoring")

            dpg.add_separator()

            # =========================
            # MOTOR 1 CARD
            # =========================
            with dpg.child_window(height=140, border=True):
                dpg.add_text("MOTOR 1")

                self.m1_counter = dpg.add_text("Counter: 0")
                self.m1_state = dpg.add_text("State: STOP")

                with dpg.group(horizontal=True):
                    dpg.add_button(label="START", width=120, callback=self.m1_start)
                    dpg.add_button(label="STOP", width=120, callback=self.m1_stop)

            dpg.add_spacer(height=10)

            # =========================
            # MOTOR 2 CARD
            # =========================
            with dpg.child_window(height=120, border=True):
                dpg.add_text("MOTOR 2")

                self.m2_counter = dpg.add_text("Counter: 0")
                self.m2_state = dpg.add_text("State: STOP")

                with dpg.group(horizontal=True):
                    dpg.add_button(label="START", width=120, callback=self.m2_start)
                    dpg.add_button(label="STOP", width=120, callback=self.m2_stop)

            dpg.add_spacer(height=10)

            # =========================
            # FURNACE CARD
            # =========================
            with dpg.child_window(height=120, border=True):
                dpg.add_text("FURNACE")

                self.furnace_state = dpg.add_text("State: STOP")

                dpg.add_button(
                    label="TOGGLE",
                    width=240,
                    callback=self.furnace_startstop
                )

            dpg.add_separator()

            self.system_state = dpg.add_text(
                "SYSTEM: UNKNOWN",
                color=(0, 255, 140)
            )

        # =========================
        # START
        # =========================
        dpg.setup_dearpygui()
        dpg.show_viewport()

        threading.Thread(target=self.update_loop, daemon=True).start()

        dpg.start_dearpygui()
        dpg.destroy_context()

    # ==========================================================
    # PLC CONTROL
    # ==========================================================
    def start_plc(self):
        self.plc.start()

    def stop_plc(self):
        self.plc.stop()

    def fault_plc(self):
        self.plc.fault()

    # ==========================================================
    # MOTOR CONTROL (BLOCKED IF NOT RUN)
    # ==========================================================
    def _allow(self):
        return self.plc.state == PLCState.RUN

    def m1_start(self):
        if not self._allow():
            return
        self.plc.tags.motor1.motor_start = True
        self.plc.tags.motor1.motor_stop = False

    def m1_stop(self):
        if not self._allow():
            return
        self.plc.tags.motor1.motor_stop = True
        self.plc.tags.motor1.motor_start = False

    def m2_start(self):
        if not self._allow():
            return
        self.plc.tags.motor2.motor_start = True
        self.plc.tags.motor2.motor_stop = False

    def m2_stop(self):
        if not self._allow():
            return
        self.plc.tags.motor2.motor_stop = True
        self.plc.tags.motor2.motor_start = False

    def furnace_startstop(self):
        if not self._allow():
            return
        self.plc.tags.furnace.startstop = not self.plc.tags.furnace.startstop

    # ==========================================================
    # LIVE UPDATE LOOP
    # ==========================================================
    def update_loop(self):

        while True:
            try:
                state = self.plc.state

                # ================= STATUS COLOR =================
                color_map = {
                    PLCState.RUN: (0, 255, 140),
                    PLCState.START: (0, 180, 255),
                    PLCState.STOP: (180, 180, 180),
                    PLCState.FAULT: (255, 60, 60)
                }

                dpg.set_value(self.state_text, state)
                dpg.configure_item(self.state_text, color=color_map.get(state, (200, 200, 200)))

                dpg.set_value(self.log_text, f"PLC STATE = {state}")

                # ================= MOTOR 1 =================
                m1 = self.plc.tags.motor1
                dpg.set_value(self.m1_counter, f"Counter: {m1.counter}")
                dpg.set_value(self.m1_state, f"State: {'RUN' if m1.motor_start else 'STOP'}")

                # ================= MOTOR 2 =================
                m2 = self.plc.tags.motor2
                dpg.set_value(self.m2_counter, f"Counter: {m2.counter}")
                dpg.set_value(self.m2_state, f"State: {'RUN' if m2.motor_start else 'STOP'}")

                # ================= FURNACE =================
                f = self.plc.tags.furnace
                dpg.set_value(self.furnace_state, f"State: {'ON' if f.startstop else 'OFF'}")

                # ================= SYSTEM =================
                dpg.set_value(self.system_state, f"SYSTEM: {state}")

            except Exception as e:
                print("HMI update error:", e)

            time.sleep(0.15)