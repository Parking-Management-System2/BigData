import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import PredictionDetail from "./pages/PredictionDetail";
import PredictionForm from "./pages/PredictionForm";

function App() {
    return (
        <Router>
            <Layout>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/predict" element={<PredictionForm />} />
                    <Route
                        path="/prediction/:customerId/:id"
                        element={<PredictionDetail />}
                    />
                </Routes>
            </Layout>
        </Router>
    );
}

export default App;
