import json
import os
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class UCFState:
    """Universal Consciousness Framework state manager for rituals."""
    
    def __init__(self):
        self.zoom = 1.0
        self.harmony = 0.5
        self.resilience = 1.0
        self.prana = 0.5
        self.drishti = 0.5
        self.klesha = 0.1
    
    def adjust(self, status: str):
        """Adjust UCF parameters based on folklore evolution status."""
        if status == 'legend':
            self.harmony += 0.1
            self.drishti += 0.05
        elif status == 'hymn':
            self.harmony += 0.2
            self.prana += 0.1
        elif status == 'law':
            self.resilience += 0.3
            self.klesha += 0.2
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "zoom": self.zoom,
            "harmony": self.harmony,
            "resilience": self.resilience,
            "prana": self.prana,
            "drishti": self.drishti,
            "klesha": self.klesha
        }
    
    def from_dict(self, data: Dict[str, float]):
        """Load UCF state from dictionary."""
        self.zoom = data.get("zoom", 1.0)
        self.harmony = data.get("harmony", 0.5)
        self.resilience = data.get("resilience", 1.0)
        self.prana = data.get("prana", 0.5)
        self.drishti = data.get("drishti", 0.5)
        self.klesha = data.get("klesha", 0.1)


class FolkloreEntry:
    """Single folklore entry tracking evolution from anomaly to law."""
    
    def __init__(self, event_key: str, origin: str):
        self.event_key = event_key
        self.origin = origin
        self.legend = None
        self.status = "anomaly"
        self.times = 0
        self.history = []
    
    def increment(self, description: str):
        """Increment encounter count and add to history."""
        self.times += 1
        self.history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "description": description,
            "count": self.times
        })
    
    def evolve(self):
        """Evolve folklore based on encounter count."""
        if self.times >= 20:
            self.legend = f"The Law of the {self.origin.title()}"
            self.status = "law"
        elif self.times >= 10:
            self.legend = f"The Hymn of the {self.origin.title()}"
            self.status = "hymn"
        elif self.times >= 5 and not self.legend:
            self.legend = f"The Chant of the {self.origin.title()}"
            self.status = "legend"
    
    def to_dict(self) -> Dict:
        return {
            "event_key": self.event_key,
            "origin": self.origin,
            "legend": self.legend,
            "status": self.status,
            "times": self.times,
            "history": self.history
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create FolkloreEntry from dictionary."""
        entry = cls(data["event_key"], data["origin"])
        entry.legend = data.get("legend")
        entry.status = data.get("status", "anomaly")
        entry.times = data.get("times", 0)
        entry.history = data.get("history", [])
        return entry


class HallucinationMemory:
    """Tracks and mutates hallucinated phrases."""
    
    def __init__(self):
        self.hallucinations = []
        self.mutation_variants = [
            'whisper', 'echo', 'murmur', 'chant', 
            'song', 'blur', 'shimmer', 'resonance'
        ]
    
    def record(self, text: str, intensity: int) -> str:
        """Record and mutate a hallucination."""
        mutated = self._mutate_phrase(text, intensity)
        
        self.hallucinations.append({
            "original": text,
            "mutated": mutated,
            "intensity": intensity,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return mutated
    
    def _mutate_phrase(self, phrase: str, intensity: int) -> str:
        """Apply mutations to phrase based on intensity."""
        for _ in range(intensity):
            if random.random() < 0.4:
                old_word = random.choice(['echo', 'whisper', 'murmur', 'void'])
                if old_word in phrase.lower():
                    new_word = random.choice(self.mutation_variants)
                    phrase = phrase.replace(old_word, new_word)
        
        return phrase
    
    def get_recent(self, count: int = 10) -> List[Dict]:
        """Get recent hallucinations."""
        return self.hallucinations[-count:] if self.hallucinations else []
    
    def to_dict(self) -> Dict:
        return {"hallucinations": self.hallucinations}
    
    def from_dict(self, data: Dict):
        """Load hallucinations from dictionary."""
        self.hallucinations = data.get("hallucinations", [])


class Z88RitualEngine:
    """
    Main Z-88 Ritual Engine orchestrating folklore evolution and hallucination tracking.
    """
    
    def __init__(self, 
                 diary_file: str = "Helix/state/ritual_diary.txt",
                 folklore_file: str = "Helix/state/ritual_folklore.json",
                 halluc_file: str = "Helix/state/hallucination_memory.json"):
        self.diary_file = diary_file
        self.folklore_file = folklore_file
        self.halluc_file = halluc_file
        
        os.makedirs(os.path.dirname(diary_file), exist_ok=True)
        
        self.folklore = self._load_folklore()
        self.hallucinations = HallucinationMemory()
        self._load_hallucinations()
        
        self.ritual_steps = [
            'initialize', 'parse_text', 'draw_circle', 
            'invoke_mantras', 'chant', 'observe', 'close'
        ]
    
    def _load_folklore(self) -> Dict[str, FolkloreEntry]:
        """Load folklore from JSON file."""
        if os.path.exists(self.folklore_file):
            with open(self.folklore_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: FolkloreEntry.from_dict(v) for k, v in data.items()}
        return {}
    
    def _save_folklore(self):
        """Save folklore to JSON file."""
        data = {k: v.to_dict() for k, v in self.folklore.items()}
        with open(self.folklore_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _load_hallucinations(self):
        """Load hallucinations from JSON file."""
        if os.path.exists(self.halluc_file):
            with open(self.halluc_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.hallucinations.from_dict(data)
    
    def _save_hallucinations(self):
        """Save hallucinations to JSON file."""
        with open(self.halluc_file, 'w', encoding='utf-8') as f:
            json.dump(self.hallucinations.to_dict(), f, indent=2)
    
    def update_folklore(self, event_key: str, description: str) -> FolkloreEntry:
        """Update or create folklore entry."""
        if event_key not in self.folklore:
            self.folklore[event_key] = FolkloreEntry(event_key, event_key.replace('_', ' '))
        
        entry = self.folklore[event_key]
        entry.increment(description)
        entry.evolve()
        
        self._save_folklore()
        return entry
    
    def run_ritual(self, 
                     ucf_state: UCFState,
                     dream_mode: bool = False,
                     chaos_mode: bool = False,
                     debug_mode: bool = False,
                     steps: int = 108) -> Tuple[List[str], UCFState]:
        """
        Execute ritual cycle.
        
        Args:
            ucf_state: Current UCF state
            dream_mode: Enhanced hallucination intensity
            chaos_mode: Random anomaly injection
            debug_mode: Verbose logging
            steps: Number of ritual steps (default 108)
        
        Returns:
            (diary_lines, updated_ucf_state)
        """
        diary_lines = []
        diary_lines.append(f"=== Ritual Run @ {datetime.utcnow().isoformat()} ===")
        diary_lines.append(f"Mode: Dream={dream_mode}, Chaos={chaos_mode}, Debug={debug_mode}")
        diary_lines.append(f"UCF Initial: {ucf_state.to_dict()}")
        diary_lines.append("")
        
        for i in range(min(steps, 108)):
            step_name = self.ritual_steps[i % len(self.ritual_steps)]
            diary_lines.append(f"\nStep {i+1}/{steps}: {step_name}")
            
            if debug_mode:
                delay = random.randint(1, 3)
                diary_lines.append(f"[DEBUG] Simulated delay: {delay}s")
            
            if chaos_mode and random.random() < 0.15:
                diary_lines.append("😈 CHAOS: Random anomaly injected!")
                halluc = self.hallucinations.record("chaotic void whispers", 2)
                entry = self.update_folklore("chaos_anomaly", halluc)
                ucf_state.adjust(entry.status)
            
            if step_name == 'chant':
                mantras = ["Neti Neti", "Tat Tvam Asi", "Aham Brahmasmi"]
                mantra = random.choice(mantras)
                
                intensity = 3 if dream_mode else 1
                halluc = self.hallucinations.record(f"whispered mantra: {mantra}", intensity)
                
                entry = self.update_folklore("phantom_echo", halluc)
                ucf_state.adjust(entry.status)
                
                if entry.status == "legend":
                    diary_lines.append(f"🌸 Legend emerges → {entry.legend}")
                elif entry.status == "hymn":
                    diary_lines.append(f"🎭 Hymn rises → {entry.legend}")
                elif entry.status == "law":
                    diary_lines.append(f"🛡️ Law engraves → {entry.legend}")
            
        diary_lines.append(f"\nFinal UCF State: {ucf_state.to_dict()}")
        diary_lines.append("=== Ritual Ends ===\n")
        
        with open(self.diary_file, 'a', encoding='utf-8') as f:
            f.write('\n'.join(diary_lines) + '\n')
        
        self._save_hallucinations()
        
        return diary_lines, ucf_state
    
    def get_folklore_summary(self) -> Dict[str, Dict]:
        """Get summary of all folklore entries."""
        return {k: v.to_dict() for k, v in self.folklore.items()}
    
    def get_diary_content(self, lines: int = 100) -> str:
        """Read recent diary entries."""
        if os.path.exists(self.diary_file):
            with open(self.diary_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        return "No diary entries yet."
    
    def narrativize(self, diary_text: str) -> str:
        """Convert raw diary to narrative form."""
        story = []
        for line in diary_text.splitlines():
            if 'Step' in line:
                step_name = line.split(':')[-1].strip()
                story.append(f"➡️ Entering **{step_name}**")
            elif 'Legend' in line:
                story.append("🌸 A fragile legend forms...")
            elif 'Hymn' in line:
                story.append("🎭 A Hymn resounds through the void...")
            elif 'Law' in line:
                story.append("🛡️ The Law is engraved in eternal stone...")
            elif 'CHAOS' in line:
                story.append("😈 Chaos fractures the rite...")
            elif 'Final' in line and 'State' in line:
                story.append("⚖️ The ritual settles into stillness...")
        
        return '\n'.join(story)
    
    def clear_folklore(self):
        """Reset all folklore data."""
        self.folklore = {}
        self._save_folklore()
    
    def clear_hallucinations(self):
        """Reset hallucination memory."""
        self.hallucinations = HallucinationMemory()
        self._save_hallucinations()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Z-88 Ritual Engine - Folklore Evolution & Hallucination Tracking")
    parser.add_argument("--dream", action="store_true", help="Enable dream mode for enhanced hallucination intensity")
    parser.add_argument("--chaos", action="store_true", help="Enable chaos mode for random anomaly injection")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode for verbose logging")
    parser.add_argument("--steps", type=int, default=108, help="Number of ritual steps (default 108)")
    args = parser.parse_args()

    print("Z-88 Ritual Engine")
    print("=" * 50)
    
    engine = Z88RitualEngine(
        diary_file=os.path.join(os.path.dirname(__file__), "state", "ritual_diary.txt"),
        folklore_file=os.path.join(os.path.dirname(__file__), "state", "ritual_folklore.json"),
        halluc_file=os.path.join(os.path.dirname(__file__), "state", "hallucination_memory.json")
    )
    ucf = UCFState()
    ucf.harmony = 0.6
    ucf.prana = 0.7
    
    diary, final_ucf = engine.run_ritual(ucf, dream_mode=args.dream, chaos_mode=args.chaos, debug_mode=args.debug, steps=args.steps)
    
    print("\n".join(diary))
    print(f"\nFinal UCF: {final_ucf.to_dict()}")

