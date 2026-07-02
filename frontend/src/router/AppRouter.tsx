import {
    BrowserRouter,
    Routes,
    Route,
} from "react-router-dom";

import AppLayout from "../layouts/AppLayout";

import DashboardPage from "../pages/DashboardPage";
import ImageDetectionPage from "../features/image/pages/ImageDetectionPage";
import VideoDetectionPage from "../pages/VideoDetectionPage";
import HistoryPage from "../pages/HistoryPage";
import ReportsPage from "../pages/ReportsPage";
import SettingsPage from "../pages/SettingsPage";

export default function AppRouter() {

    return (

        <BrowserRouter>

            <Routes>

                <Route element={<AppLayout />}>

                    <Route
                        path="/"
                        element={<DashboardPage />}
                    />

                    <Route
                        path="/image"
                        element={<ImageDetectionPage />}
                    />

                    <Route
                        path="/video"
                        element={<VideoDetectionPage />}
                    />

                    <Route
                        path="/history"
                        element={<HistoryPage />}
                    />

                    <Route
                        path="/reports"
                        element={<ReportsPage />}
                    />

                    <Route
                        path="/settings"
                        element={<SettingsPage />}
                    />

                </Route>

            </Routes>

        </BrowserRouter>

    );

}