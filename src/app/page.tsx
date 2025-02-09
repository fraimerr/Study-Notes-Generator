export default function Home() {
	return (
		<div className="flex flex-col h-screen w-screen items-center justify-center py-6">
			<h1 className="text-4xl font-bold mb-6">Study Notes Gen from PDF</h1>
			<form className="flex flex-col items-center mb-6">
				<label
					htmlFor="file"
					className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
				>
					Select a file
				</label>
			</form>
		</div>
	);
}
