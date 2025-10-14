import Image from "next/image";
import Navbar from "./components/Navbar";
import SearchForm from "./components/queryInput";
export default function Home() {
  return (
    <div>
       <Navbar />
      Recommend Me Claude
      <SearchForm />
    </div>
  );
}
