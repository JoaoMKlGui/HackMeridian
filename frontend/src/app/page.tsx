import Link from "next/link";

export default function Home() {
  return (
    <main className="mt-[100px] flex flex-col min-h-[calc(100vh-100px)] justify-center p-2">
      <div className="flex flex-col items-center  w-full h-full ">
        <div className="flex flex-col items-center gap-4">
          <h1 className="hero-title">
            <span className="text-primary-pink">NOT</span>
            <span className="text-primary-blue">Gambling</span>
          </h1>
          <p className="hero-subtitle">Fairness. Distributed.</p>
        </div>
      </div>
      <Link
        className="btn btn-primary mt-20 flex justify-center items-center w-fit mx-auto hero-button"
        href="/create"
      >
        Begin 
      </Link>
    </main>
  );
}
