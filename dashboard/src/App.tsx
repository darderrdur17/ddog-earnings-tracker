import { motion } from "framer-motion";
import { CallConstruction } from "./components/CallConstruction";
import { GrowthChart } from "./components/GrowthChart";
import { Header } from "./components/Header";
import { KpiRow } from "./components/KpiRow";
import { LeadLag } from "./components/LeadLag";
import { SignalChart } from "./components/SignalChart";
import { Sources } from "./components/Sources";
import { StubNowcast } from "./components/StubNowcast";
import { Validation } from "./components/Validation";
import { summary } from "./data";

const fade = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0 },
};

export default function App() {
  return (
    <div className="min-h-screen bg-ink-950 text-zinc-100">
      <div className="mx-auto max-w-[1280px] px-4 py-6 sm:px-6 lg:px-8">
        <Header />
        <KpiRow />
        <StubNowcast />

        <motion.section
          className="mt-6 grid gap-4 lg:grid-cols-2"
          initial="hidden"
          animate="show"
          variants={{ show: { transition: { staggerChildren: 0.08, delayChildren: 0.35 } } }}
        >
          <motion.div variants={fade}>
            <GrowthChart />
          </motion.div>
          <motion.div variants={fade}>
            <SignalChart />
          </motion.div>
        </motion.section>

        <motion.section
          className="mt-4 grid gap-4 lg:grid-cols-12"
          initial="hidden"
          animate="show"
          variants={{ show: { transition: { staggerChildren: 0.08, delayChildren: 0.5 } } }}
        >
          <motion.div className="lg:col-span-5" variants={fade}>
            <CallConstruction />
          </motion.div>
          <motion.div className="lg:col-span-4" variants={fade}>
            <LeadLag />
          </motion.div>
          <motion.div className="lg:col-span-3" variants={fade}>
            <Validation />
          </motion.div>
        </motion.section>

        <Sources asOf={summary.as_of_utc} npmEnd={summary.npm_end} />
      </div>
    </div>
  );
}
