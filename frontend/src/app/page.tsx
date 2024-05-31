"use client";

import { ChangeEvent, FormEvent, useState } from "react";
import ReactMarkdown from "react-markdown";

export default function Home() {
	const [file, setFile] = useState<File | null>(null);
	const [notes, setNotes] = useState<string>("");

	const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
		if (event.target.files) {
			setFile(event.target.files[0]);
			console.log(`Selected file: ${event.target.files[0].name}`);
		}
	};

	const handleSubmit = async (event: FormEvent) => {
		event.preventDefault();
		if (!file) {
			console.error("No file selected");
			return;
		}

		const formData = new FormData();
		formData.append("file", file);

		try {
			console.log("Sending file to server...");
			const response = await fetch("http://127.0.0.1:5000/generate_notes", {
				method: "POST",
				body: formData,
			});

			const res = await response.json();

			console.log("Response from server:", res);

			if (response.ok) {
				setNotes(res.notes);
			} else {
				console.error(res.error);
			}
		} catch (err) {
			console.error("Error submitting file:", err);
		}
	};

	return (
		<div className="flex flex-col items-center justify-center min-h-screen py-6">
			<h1 className="text-4xl font-bold mb-6">Generate Study Notes</h1>
			<form onSubmit={handleSubmit} className="flex flex-col items-center mb-6">
				<label
					htmlFor="file-upload"
					className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded cursor-pointer mb-2"
				>
					Select File
				</label>
				<input
					id="file-upload"
					type="file"
					onChange={handleFileChange}
					className="hidden"
				/>
				<button
					type="submit"
					className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
				>
					Generate Notes
				</button>
			</form>
			<div className="max-w-3xl">
				<h2 className="text-2xl font-bold mb-2">Generated Notes:</h2>
				<ReactMarkdown className="border border-white p-4 rounded-md whitespace-pre-wrap">
					{notes}
				</ReactMarkdown>
			</div>
		</div>
	);
}
