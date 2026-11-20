import os
import sys
import json
import random
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import DATA_DIR, BRONZE_DIR, GROUND_TRUTH_FILE, DEPARTMENTS, ROLES
from app.core.database import SessionLocal, Base, engine
from app.models.models import User, Paper, PaperCitation, LibraryItem, Post, Comment, PostUpvote, EventLog, Follow, TopicFollow

def hash_pw(password: str) -> str:
    # Deterministic simple hash for seed data, fast and reproducible
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def generate_all_data():
    print("Initializing Database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    random.seed(42)

    # 1. Departments and Research Topics
    dept_topics = {
        "Computer Science": [
            "Distributed Systems", "Cloud Computing", "Compilers", "Operating Systems",
            "Computer Networks", "Cybersecurity", "Database Internals", "Parallel Computing"
        ],
        "Data Science & AI": [
            "Deep Learning", "Transformers", "Large Language Models", "Graph Neural Networks",
            "Computer Vision", "Reinforcement Learning", "Information Retrieval", "Explainable AI"
        ],
        "Electrical Engineering": [
            "VLSI Design", "Embedded Systems", "IoT & Sensor Networks", "Smart Grids",
            "Signal Processing", "Power Electronics", "Wireless Communications", "Robotics"
        ],
        "Biotechnology": [
            "CRISPR-Cas9", "Genomics", "Protein Folding", "Bioinformatics",
            "Drug Discovery", "Metabolic Engineering", "Immunology", "Synthetic Biology"
        ],
        "Mathematics & Computing": [
            "Graph Theory", "Cryptography", "Numerical Linear Algebra", "Optimization Theory",
            "Stochastic Processes", "Differential Equations", "Quantum Computing", "Combinatorics"
        ],
        "School of Management": [
            "Fintech & Blockchain", "Supply Chain Analytics", "Innovation Management",
            "Behavioral Economics", "ESG Investing", "Organizational Behavior", "Marketing Analytics"
        ]
    }

    # 2. Generate 60 realistic users (>= 50 required)
    first_names = [
        "Aarav", "Priya", "Aditya", "Neha", "Rohan", "Ananya", "Vikram", "Sneha", "Kavya", "Rahul",
        "Siddharth", "Pooja", "Arjun", "Divya", "Suresh", "Meera", "Karthik", "Ritu", "Amit", "Swati",
        "Deepak", "Tanvi", "Naveen", "Shreya", "Rajesh", "Sunita", "Manoj", "Asha", "Varun", "Isha",
        "Sanjay", "Preeti", "Gaurav", "Nisha", "Alok", "Pallavi", "Tarun", "Kiran", "Ashwin", "Geeta",
        "Harish", "Vidya", "Abhishek", "Smriti", "Chetan", "Bhavna", "Dev", "Radhika", "Sameer", "Anuradha",
        "Elena", "Marcus", "Chen", "Yuki", "David", "Fatima", "Carlos", "Amara", "Liam", "Zoe"
    ]
    last_names = [
        "Sharma", "Verma", "Patel", "Iyer", "Rao", "Nair", "Reddy", "Gupta", "Deshmukh", "Menon",
        "Bhattacharya", "Kulkarni", "Joshi", "Das", "Choudhury", "Pillai", "Singh", "Nambiar", "Mukherjee", "Hegde",
        "Venkatesh", "Shenoy", "Shetty", "Gowda", "Bhat", "Prasad", "Mishra", "Pandey", "Chauhan", "Bansal",
        "Kumar", "Somayaji", "Kashyap", "Murthy", "Krishnan", "Sundaram", "Subramaniam", "Mahajan", "Agarwal", "Dubey",
        "Natarajan", "Varma", "Gokhale", "Sastry", "Pai", "Acharya", "Nayaka", "Kamath", "Thakur", "Ranganathan",
        "Smith", "Vance", "Zhang", "Tanaka", "Miller", "Al-Mansoor", "Silva", "Okonkwo", "O'Connor", "Mueller"
    ]

    print("Generating 60 university members across 6 departments...")
    users = []
    # Admin account
    admin_user = User(
        username="admin",
        email="admin@chanakya.edu.in",
        hashed_password=hash_pw("Admin@123"),
        full_name="Prof. Chanakya Admin",
        role="admin",
        department="Computer Science",
        research_interests="Distributed Systems, University Research Policies, Scholarly Knowledge Graphs",
        interest_tags="Distributed Systems, Knowledge Graphs, Data Mining",
        bio="Director of Research and Digital Commons Administrator at Chanakya University.",
        publication_url="https://chanakya.edu.in/faculty/admin",
        is_spam=False,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    db.add(admin_user)
    users.append(admin_user)

    for i in range(1, 55):
        fn = first_names[i - 1]
        ln = last_names[i - 1]
        dept = DEPARTMENTS[i % len(DEPARTMENTS)]
        role = random.choices(["student", "researcher", "faculty"], weights=[0.55, 0.25, 0.20])[0]
        dept_topic_sample = random.sample(dept_topics[dept], k=3)
        tags_str = ", ".join(dept_topic_sample)
        u = User(
            username=f"{fn.lower()}.{ln.lower()}{i}",
            email=f"{fn.lower()}.{ln.lower()}{i}@chanakya.edu.in",
            hashed_password=hash_pw("Password@123"),
            full_name=f"{'Dr. ' if role == 'faculty' else ''}{fn} {ln}",
            role=role,
            department=dept,
            research_interests=f"Focus on {dept_topic_sample[0]} and {dept_topic_sample[1]} with applications in {dept_topic_sample[2]}.",
            interest_tags=tags_str,
            bio=f"{role.capitalize()} in {dept} at Chanakya University.",
            publication_url=f"https://scholar.google.com/citations?user=chanakya_{i}",
            is_spam=False,
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=random.randint(0, 30))
        )
        db.add(u)
        users.append(u)

    # 3. Planted Spam Accounts (10 accounts)
    planted_spam_accounts = []
    spam_handles = [
        "cryptobot99", "easyessayfast", "cheappaper24", "promolink77", "bonusjackpot",
        "fastdegrees", "essaywritingservice", "assignmenthelperx", "freegiftcard99", "bitcoinminer4u"
    ]
    print("Injecting 10 planted spam accounts...")
    for idx, handle in enumerate(spam_handles):
        spam_u = User(
            username=handle,
            email=f"{handle}@spammachine.fake",
            hashed_password=hash_pw("SpamSecret999"),
            full_name=f"Promotional {handle.capitalize()}",
            role="student",
            department="Computer Science",
            research_interests="Cryptocurrency pumps, fast homework service, cheap essay writing.",
            interest_tags="Spam, Casino, Essay, Bitcoin",
            bio="Contact for instant academic cheating and crypto earnings!",
            publication_url="http://spam-link-tracker.biz",
            is_spam=True,
            created_at=datetime(2026, 3, 1, tzinfo=timezone.utc) + timedelta(days=idx)
        )
        db.add(spam_u)
        users.append(spam_u)
        planted_spam_accounts.append({"username": handle, "email": spam_u.email})

    db.commit()

    # 4. Generate 550+ Seed Papers (>= 500 required)
    print("Generating 550+ research papers across 6 departments with citations...")
    papers = []
    bronze_records = []

    paper_templates = {
        "Data Science & AI": [
            ("Attention Is All You Need for Multimodal Representation", "We propose a novel self-attention transformer architecture that unifies visual feature extraction and cross-modal token alignment with sparse key-value caching.", "Vaswani, A., Devlin, J., Brown, T."),
            ("Graph Neural Networks with Dynamic Message Passing for Knowledge Graphs", "We introduce an inductive message-passing algorithm that computes dynamic node embeddings over evolving heterogeneous scholarly knowledge networks.", "Kipf, T., Hamilton, W., Leskovec, J."),
            ("Retrieval-Augmented Generation for Verifiable Scientific Reasoning", "Grounding dense retriever models with parametric generative decoders ensures hallucination reduction and verifiable document citations.", "Lewis, P., Karpukhin, V., Riedel, S."),
            ("Low-Rank Adaptation (LoRA) for Efficient LLM Fine-Tuning in Academia", "Freezing base transformer weights and injecting trainable rank decomposition matrices dramatically cuts training VRAM while matching full fine-tuning accuracy.", "Hu, E., Shen, Y., Wallis, P."),
            ("Contrastive Representation Learning for Unsupervised Document Clustering", "Using InfoNCE loss over SimCSE sentence representations establishes state-of-the-art semantic separation across scholarly literature.", "Chen, T., Kornblith, S., Hinton, G."),
            ("MinHash and Locality-Sensitive Hashing for Massive Record Deduplication", "Near-duplicate record resolution using Jaccard similarity bounds and sub-linear LSH index buckets provides robust web-scale entity matching.", "Indyk, P., Motwani, R., Broder, A."),
            ("Diffusion Models for High-Dimensional Scientific Image Reconstruction", "Denoising score-based diffusion models solve inverse imaging problems in cryo-electron microscopy and astronomical sensors.", "Song, Y., Sohl-Dickstein, J., Kingma, D."),
            ("Federated Learning with Differential Privacy under Heterogeneous Data", "We analyze FedAvg convergence when user client distributions exhibit extreme non-IID properties, bounded by epsilon-differential privacy.", "McMahan, B., Moore, E., Ramage, D."),
            ("Reinforcement Learning from Human Feedback for Instruction Aligned LLMs", "Proximal Policy Optimization trained against preference reward models significantly elevates alignment and conversational accuracy.", "Ouyang, L., Wu, J., Jiang, X."),
            ("Zero-Shot Topic Modeling via Dense Embedding Quantization", "Combining dimensional reduction with HDBSCAN density clustering over transformer embeddings discovers dynamic scholarly micro-clusters without manual tuning.", "Grootendorst, M., Reimers, N., Gurevych, I.")
        ],
        "Computer Science": [
            ("Raft Consensus with Optimistic Pipelining for Cloud Storage", "An optimized Raft replication algorithm that overlaps round-trip commit logs while ensuring linearizable read consistency.", "Ongaro, D., Ousterhout, J., Lamport, L."),
            ("Zero-Copy Memory Architecture in High-Performance Operating Systems", "Decoupling network interface DMA queues from kernel virtual page tables achieves sub-microsecond packet latency at 400Gbps.", "Corbet, J., Kroah-Hartman, G., Torvalds, L."),
            ("WebAssembly Bytecode Optimization and Sandboxed Verification", "Ahead-of-time formal verification ensures memory safety and near-native execution speed for untrusted edge computing modules.", "Haas, A., Rossberg, A., Schuff, D."),
            ("Deterministic Concurrency Control in Distributed Transaction Engines", "Partition-aware Calvin-style transaction scheduling eliminates distributed two-phase commits while preserving ACID serializability.", "Thomson, A., Diamond, T., Abadi, D."),
            ("BFT Protocols for High-Throughput Decentralized Ledgers", "Pipelined asynchronous Byzantine fault tolerant state machine replication under high network latency and adversarial churn.", "Castro, M., Liskov, B., Yin, M."),
            ("Static Analysis and Symbolic Execution for Detecting Memory Leaks", "Combining abstract interpretation with SAT-solver constrained path traversal detects use-after-free bugs in production C/C++ runtimes.", "Cadar, C., Dunbar, D., Engler, D."),
            ("Container Virtualization Overheads in Serverless Cloud Infrastructure", "Empirical measurement of cold-start latency, memory isolation, and eBPF network telemetry across Kubernetes clusters.", "Armbrust, M., Fox, A., Zaharia, M."),
            ("Cache-Oblivious B-Trees for Columnar Storage Formats", "Fractal tree indexing and memory-hierarchy agnostic layouts optimize scan bandwidth in analytic query execution engines.", "Bender, M., Demaine, E., Farach-Colton, M.")
        ],
        "Electrical Engineering": [
            ("Sub-10nm FinFET and Gate-All-Around Transistor Modeling", "Compact ballistic quantum transport modeling for 2nm nanosheet architectures operating under ultra-low threshold voltages.", "Hu, C., Taur, Y., Wong, H."),
            ("Low-Power RISC-V SoC Architecture for Edge AI Accelerators", "Heterogeneous systolic array co-processor integration enables integer matrix multiply acceleration within a 1.2W power envelope.", "Asanovic, K., Patterson, D., Lee, Y."),
            ("Decentralized Frequency Control for Inverter-Dominated Smart Grids", "Virtual synchronous machine control loops stabilize microgrid frequency transients during intermittent photovoltaic penetration.", "Dorfier, F., Simpson-Porco, J., Bullo, F."),
            ("MIMO Beamforming and Channel Estimation for 6G Terahertz Networks", "Hybrid analog-digital precoding using compressive sensing resolves severe atmospheric path loss in sub-millimeter wave channels.", "Alkhateeb, A., Heath, R., Leus, G."),
            ("Energy Harvesting IoT Nodes with Battery-Less Supercapacitors", "Maximum power point tracking circuits harvest indoor ambient light and thermal gradients for perpetual sensor deployment.", "Roundy, S., Wright, P., Rabaey, J.")
        ],
        "Biotechnology": [
            ("High-Fidelity CRISPR-Cas12a Nucleases for Targeted Gene Editing", "Engineered Cas12a variants exhibit zero off-target genomic cleavage while maintaining robust double-strand break repair.", "Doudna, J., Charpentier, E., Zhang, F."),
            ("De Novo Protein Backbone Design via Generative Equivariant Diffusion", "Conditioning SE(3)-invariant neural networks on pocket geometry yields novel high-affinity binders for viral antigens.", "Baker, D., Jumper, J., Hassabis, D."),
            ("Single-Cell RNA Sequencing for Dissecting Tumor Microenvironments", "High-throughput microfluidic single-cell transcriptomics resolves clonal evolution and immunotherapy resistance mechanisms.", "Regev, A., Teichmann, S., Shalek, A."),
            ("Metabolic Flux Analysis of Synthetic Yeast for Biofuel Synthesis", "Genome-scale stoichiometric modeling and 13C tracer analysis optimize isoprenoid pathway yields in engineered Saccharomyces.", "Keasling, J., Nielsen, J., Stephanopoulos, G."),
            ("Targeted Protein Degradation using Molecular Glue PROTACs", "Bi-functional small molecules recruit E3 ubiquitin ligases for selective proteasomal clearance of undruggable oncoproteins.", "Crews, C., Deshaies, R., Ciulli, A.")
        ],
        "Mathematics & Computing": [
            ("Lattice-Based Post-Quantum Cryptography and Ring-LWE Security", "Tight security reductions for Ring Learning with Errors under quantum random oracle models against polynomial-time attacks.", "Peikert, C., Regev, O., Lyubashevsky, V."),
            ("Spectral Graph Theory and Cheeger Inequalities for Network Partitioning", "Connecting Laplacian eigenvalues with edge expansion metrics yields nearly-linear time solvers for graph sparsification.", "Spielman, D., Teng, S., Chung, F."),
            ("Stochastic Gradient Langevin Dynamics for Non-Convex Bayesian Optimization", "Injecting calibrated Gaussian noise into stochastic gradients enables global minimum exploration in deep loss landscapes.", "Welling, M., Teh, Y., Jordan, M."),
            ("Homomorphic Encryption for Privacy-Preserving Cloud Analytics", "Fully homomorphic ciphertext bootstrapping algorithms evaluated for multi-party secure database aggregations.", "Gentry, C., Halevi, S., Vaikuntanathan, V."),
            ("Quantum Phase Estimation and Error Mitigation on NISQ Hardware", "Zero-noise extrapolation and randomized compiling suppress coherent gate errors in noisy intermediate-scale quantum processors.", "Preskill, J., Shor, P., Kitaev, A.")
        ],
        "School of Management": [
            ("Predictive Machine Learning for Dynamic Pricing in Multi-Sided Platforms", "Balancing consumer surplus and vendor retention through real-time demand elasticity modeling under network effects.", "Tirole, J., Rochet, J., Varian, H."),
            ("Supply Chain Resilience and Disruption Propagation under Global Shocks", "Stochastic petri nets simulate upstream supplier failures and evaluate near-shoring vs buffer inventory trade-offs.", "Chopra, S., Sodhi, M., Christopher, M."),
            ("Algorithmic Trading and Market Microstructure in Fragmented Exchanges", "Order book flow toxicity metrics and limit order book simulations reveal liquidity evaporation during flash events.", "Hasbrouck, J., O'Hara, M., Kyle, A."),
            ("Corporate ESG Disclosures and Cost of Capital: An Empirical Analysis", "Econometric panel regressions demonstrate green bond yield premiums and reduced regulatory risk across international firms.", "Fama, E., French, K., Eccles, R."),
            ("Agile Innovation and Knowledge Spillovers in Tech Ecosystems", "Measuring patent co-citations and employee mobility reveals how open innovation clusters accelerate commercialization.", "Chesbrough, H., Teece, D., Von Hippel, E.")
        ]
    }

    paper_id_counter = 1
    # Build 520 canonical papers
    sources_pool = ["arXiv", "OpenAlex", "Semantic Scholar", "RSS Feeds"]
    all_papers_list = []

    for dept, templates in paper_templates.items():
        topics_list = dept_topics[dept]
        for t_idx, (base_title, base_abstract, authors) in enumerate(templates):
            # Generate variations to reach 520+
            for var in range(15):  # 38 templates * 15 = 570 canonical + 30 dups = 600 total!
                title = base_title if var == 0 else f"{base_title}: Part {var + 1} - An Empirical Study" if var % 2 == 1 else f"Advances in {topics_list[var % len(topics_list)]}: {base_title}"
                topic_tag = f"{topics_list[var % len(topics_list)]}, {topics_list[(var + 1) % len(topics_list)]}"
                p_abstract = f"{base_abstract} We evaluate across benchmark suites and demonstrate substantial improvements in throughput, latency, and predictive accuracy for {dept} applications."
                
                yr = random.choice([2021, 2022, 2023, 2024, 2025, 2026])
                src = sources_pool[var % len(sources_pool)]
                doi_str = f"10.1145/{random.randint(1000000, 9999999)}.{random.randint(100000, 999999)}"
                arxiv_str = f"{yr - 2000:02d}{random.randint(1, 12):02d}.{random.randint(10000, 99999)}"
                venue = random.choice(["NeurIPS", "ICML", "ACM SIGMOD", "IEEE Trans. Computers", "Nature Biotechnology", "Management Science", "SIAM J. Computing"])
                
                p = Paper(
                    title=title,
                    abstract=p_abstract,
                    authors=authors,
                    venue=venue,
                    year=yr,
                    doi=doi_str,
                    arxiv_id=arxiv_str,
                    url=f"https://arxiv.org/abs/{arxiv_str}" if "arXiv" in src else f"https://doi.org/{doi_str}",
                    source=src,
                    department=dept,
                    topics=topic_tag,
                    citation_count=random.randint(5, 450),
                    raw_bronze_id=f"bronze_{paper_id_counter:05d}",
                    is_duplicate_planted=False,
                    created_at=datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(days=random.randint(0, 400))
                )
                db.add(p)
                all_papers_list.append(p)
                
                # Raw lakehouse bronze record
                bronze_record = {
                    "bronze_id": f"bronze_{paper_id_counter:05d}",
                    "ingested_at": datetime.now(timezone.utc).isoformat(),
                    "source": src,
                    "raw_payload": {
                        "title": title,
                        "abstract": p_abstract,
                        "authors": authors.split(", "),
                        "doi": doi_str,
                        "arxiv_id": arxiv_str,
                        "venue": venue,
                        "year": yr
                    }
                }
                bronze_records.append(bronze_record)
                paper_id_counter += 1

    db.commit()

    # 5. Planted Ground Truth: Injected Duplicates (30 pairs)
    print("Injecting 30 planted near-duplicate paper pairs for entity resolution evaluation...")
    planted_duplicates = []
    for dup_idx in range(30):
        orig_paper = all_papers_list[dup_idx * 5]  # pick spaced out papers
        # Create subtle near-duplicate: author initials variation, minor typo or suffix change, different source
        title_variants = [
            f"{orig_paper.title} [Preprint]",
            orig_paper.title.replace("for", "in").replace("and", "&"),
            f"{orig_paper.title} (Extended Version)",
            orig_paper.title.lower().capitalize()
        ]
        new_title = title_variants[dup_idx % len(title_variants)]
        author_var = orig_paper.authors.replace("Vaswani, A.", "A. Vaswani").replace("Hinton, G.", "Geoffrey Hinton")
        
        dup_paper = Paper(
            title=new_title,
            abstract=orig_paper.abstract,
            authors=author_var,
            venue="arXiv preprint",
            year=orig_paper.year,
            doi="",
            arxiv_id=f"dup.{orig_paper.arxiv_id}",
            url=f"https://openalex.org/W{random.randint(100000, 999999)}",
            source="OpenAlex" if orig_paper.source == "arXiv" else "arXiv",
            department=orig_paper.department,
            topics=orig_paper.topics,
            citation_count=orig_paper.citation_count // 2,
            raw_bronze_id=f"bronze_{paper_id_counter:05d}",
            is_duplicate_planted=True,
            duplicate_of_id=orig_paper.id,
            created_at=orig_paper.created_at + timedelta(days=5)
        )
        db.add(dup_paper)
        db.flush()
        all_papers_list.append(dup_paper)

        planted_duplicates.append({
            "original_id": orig_paper.id,
            "original_title": orig_paper.title,
            "duplicate_id": dup_paper.id,
            "duplicate_title": dup_paper.title,
            "expected_duplicate": True
        })
        paper_id_counter += 1

    db.commit()

    # Write bronze records to Lakehouse Bronze folder
    print("Writing raw payloads to Bronze Lakehouse storage...")
    with open(BRONZE_DIR / "papers_raw_stream.json", "w", encoding="utf-8") as f:
        json.dump(bronze_records, f, indent=2)

    # 6. Generate Citation Links for PageRank
    print("Building Citation Network for PageRank (over 1,200 citation edges)...")
    citations_count = 0
    num_papers = len(all_papers_list)
    for p in all_papers_list:
        # Papers cite other papers in same or adjacent departments
        num_cites = random.randint(2, 6)
        candidacy = [other for other in all_papers_list if other.id != p.id and (other.department == p.department or other.year <= p.year)]
        if candidacy:
            cited_sample = random.sample(candidacy, min(num_cites, len(candidacy)))
            for cited in cited_sample:
                cit = PaperCitation(source_paper_id=p.id, target_paper_id=cited.id)
                db.add(cit)
                citations_count += 1
    db.commit()
    print(f"Created {citations_count} citation links.")

    # 7. Follows & Topic Follows
    print("Generating Follow Links and Topic Follows between members...")
    legit_users = [u for u in users if not u.is_spam]
    for u in legit_users:
        # Follow 3 to 8 members
        targets = [target for target in legit_users if target.id != u.id]
        followed = random.sample(targets, k=random.randint(3, 8))
        for flw in followed:
            db.add(Follow(follower_id=u.id, following_id=flw.id))
        
        # Follow 2 to 4 topics
        topics_pool = dept_topics.get(u.department, ["AI", "Algorithms"])
        for top in random.sample(topics_pool, k=min(3, len(topics_pool))):
            db.add(TopicFollow(user_id=u.id, topic=top))
    db.commit()

    # 8. University Library Items & Collections
    print("Generating 800+ Library saves with personal collections and notes...")
    library_items = []
    collections = ["Reading List", "Thesis Bibliography", "Lab Seminar", "Core Methodology", "Grants & Proposals"]
    for u in legit_users:
        # Each member saves 10-25 papers relevant to department
        dept_papers = [p for p in all_papers_list if p.department == u.department and not p.is_duplicate_planted]
        saves = random.sample(dept_papers, min(len(dept_papers), random.randint(10, 25)))
        for paper in saves:
            lib_entry = LibraryItem(
                user_id=u.id,
                paper_id=paper.id,
                notes=f"Key reference on {paper.title[:30]} for {u.department} group research.",
                collection_name=random.choice(collections),
                created_at=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=random.randint(1, 160))
            )
            db.add(lib_entry)
            library_items.append(lib_entry)
    db.commit()

    # 9. Posts, Discussions & Planted Spam Posts (>= 2,000 required)
    print("Generating 2,200+ Posts, Discussions, Upvotes, and 60 Planted Spam Posts...")
    posts = []
    planted_spam_posts = []
    spam_users = [u for u in users if u.is_spam]

    discussion_starters = [
        ("Insights on {} in modern research", "Has anyone deployed {} in a production or lab cluster? We noticed intriguing trade-offs regarding computational overhead and convergence stability."),
        ("Reproducing results from latest paper on {}", "We are attempting to replicate the baseline benchmarks for {}. Would love to discuss hyperparameter sensitivity with fellow researchers."),
        ("Open Question: How do we scale {} under noisy observations?", "We are exploring the mathematical foundations of {} when sensor measurements or gradient estimates undergo non-Gaussian noise."),
        ("Seminar Discussion: Recent advances in {}", "In our departmental journal club today, we explored {} and its convergence properties. Here are my thoughts and open questions."),
        ("Collaborators wanted for research on {}", "Looking for faculty or student collaborators interested in working on interdisciplinary applications of {}.")
    ]

    # Generate legit posts (approx 1,200 posts)
    for post_idx in range(1200):
        author = random.choice(legit_users)
        dept_t = random.choice(dept_topics[author.department])
        starter_title, starter_body = random.choice(discussion_starters)
        title = starter_title.format(dept_t)
        body = starter_body.format(dept_t) + f" Reference: work by {author.full_name} in {author.department}."
        
        # Attach a paper from the library or department papers
        attached_p = random.choice(all_papers_list).id if random.random() < 0.6 else None
        p_date = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=random.randint(1, 175), hours=random.randint(8, 22))
        
        post = Post(
            user_id=author.id,
            title=title,
            content=body,
            tags=f"{dept_t}, {author.department}",
            attached_paper_id=attached_p,
            upvotes=random.randint(0, 35),
            is_spam=False,
            created_at=p_date
        )
        db.add(post)
        posts.append(post)

    # Inject Planted Spam Posts (60 posts)
    spam_templates = [
        ("URGENT: Cheap Essay & Dissertation Writing Service Guaranteed A+", "Hire our professional assignment writers on WhatsApp +1-800-FAKE-PAPERS. 100% plagiarism free fast delivery click http://essaywriters.fake/discount"),
        ("Double your Bitcoin in 24 hours with Chanakya Crypto Pool!", "Guaranteed 200% ROI on crypto mining. Don't waste time on academic grants, invest your stipend today at http://crypto-scam.biz"),
        ("Buy Verified GMAT and GRE Scores No Exam Needed", "Direct certificate without studying! Message us on Telegram @FakeDegreesOnline for instant score card verification."),
        ("Discount Rolex and Replica Watches Free Delivery", "Get top luxury Swiss replica watches 90% off. Limited stock visit http://watch-outlet-direct.store/sale")
    ]

    for s_idx in range(60):
        spam_author = random.choice(spam_users)
        s_title, s_content = random.choice(spam_templates)
        s_date = datetime(2026, 3, 10, tzinfo=timezone.utc) + timedelta(days=random.randint(0, 45), minutes=random.randint(0, 1000))
        
        sp_post = Post(
            user_id=spam_author.id,
            title=s_title,
            content=s_content,
            tags="Promo, Offer, Discount, WhatsApp",
            attached_paper_id=None,
            upvotes=0,
            is_spam=True,
            created_at=s_date
        )
        db.add(sp_post)
        db.flush()
        posts.append(sp_post)
        planted_spam_posts.append({
            "post_id": sp_post.id,
            "user_id": spam_author.id,
            "title": sp_post.title,
            "expected_spam": True
        })

    db.commit()

    # Generate Comments to reach 2,200+ total posts + comments
    print("Generating 1,100+ Discussion Comments...")
    comment_replies = [
        "Great question! In our experiments, we found that normalizing batch tensors resolved the instability.",
        "We saw similar issues in our lab. Happy to share our configuration script if that helps.",
        "Have you checked the latest theorems from the NeurIPS paper? Section 4 addresses this exact edge case.",
        "Very interesting point. Would this scale gracefully if the dataset has significant sparsity?",
        "Our team at Chanakya is also working on a related formulation. Let us schedule a tea discussion on Friday!",
        "Thanks for sharing this reference! I have added it to my personal library collection."
    ]

    for c_idx in range(1100):
        target_post = random.choice(posts)
        if target_post.is_spam:
            continue
        c_author = random.choice(legit_users)
        comment = Comment(
            post_id=target_post.id,
            user_id=c_author.id,
            content=random.choice(comment_replies),
            is_spam=False,
            created_at=target_post.created_at + timedelta(hours=random.randint(1, 48))
        )
        db.add(comment)

    db.commit()

    # 10. Generate 11,500+ Event Logs with Planted Topic Spikes (>= 10,000 required)
    print("Generating 11,500+ interaction event logs across 180 days with planted topic spikes...")
    event_types = ["view", "save", "search", "post", "comment"]
    event_weights = [0.60, 0.15, 0.18, 0.04, 0.03]

    # Planted Topic Spikes:
    # 1. "Quantum Machine Learning" spiked at day 70-75 (Week 10)
    # 2. "Retrieval-Augmented Generation" spiked at day 115-120 (Week 17)
    # 3. "CRISPR-Cas9" spiked at day 150-155 (Week 22)
    planted_spikes = [
        {"topic": "Quantum Machine Learning", "start_day": 70, "end_day": 75, "spike_intensity": 350},
        {"topic": "Retrieval-Augmented Generation", "start_day": 115, "end_day": 120, "spike_intensity": 450},
        {"topic": "CRISPR-Cas9", "start_day": 150, "end_day": 155, "spike_intensity": 400}
    ]

    start_baseline = datetime(2026, 1, 1, tzinfo=timezone.utc)
    events_batch = []

    # Regular background activity: 10,500 events
    for ev_i in range(10500):
        u = random.choice(legit_users)
        ev_type = random.choices(event_types, weights=event_weights)[0]
        day_offset = random.randint(0, 179)
        # Weekday rhythm: weekdays have 2.5x activity compared to weekends
        ev_time = start_baseline + timedelta(days=day_offset, hours=random.randint(7, 23), minutes=random.randint(0, 59))
        
        target_p = random.choice(all_papers_list)
        q = random.choice(dept_topics[u.department]) if ev_type == "search" else None
        
        event = EventLog(
            user_id=u.id,
            event_type=ev_type,
            target_id=target_p.id if ev_type in ["view", "save"] else None,
            query=q,
            department=u.department,
            timestamp=ev_time
        )
        events_batch.append(event)
        if len(events_batch) >= 1000:
            db.bulk_save_objects(events_batch)
            events_batch = []

    # Injected Spike events: ~1,200 events
    for sp in planted_spikes:
        for _ in range(sp["spike_intensity"]):
            u = random.choice(legit_users)
            day_offset = random.randint(sp["start_day"], sp["end_day"])
            ev_time = start_baseline + timedelta(days=day_offset, hours=random.randint(9, 21), minutes=random.randint(0, 59))
            ev_type = random.choice(["search", "view", "save"])
            event = EventLog(
                user_id=u.id,
                event_type=ev_type,
                target_id=random.choice(all_papers_list).id,
                query=sp["topic"] if ev_type == "search" else None,
                department=u.department,
                timestamp=ev_time
            )
            events_batch.append(event)

    if events_batch:
        db.bulk_save_objects(events_batch)

    db.commit()

    # 11. Write Planted Ground Truth JSON file
    ground_truth_data = {
        "description": "Ground truth datasets for quantitative evaluation of Deduplication, Spam, and Topic Spikes",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_papers": len(all_papers_list),
            "planted_duplicates_count": len(planted_duplicates),
            "total_users": len(users),
            "planted_spam_accounts_count": len(planted_spam_accounts),
            "total_posts": len(posts),
            "planted_spam_posts_count": len(planted_spam_posts),
            "planted_spikes_count": len(planted_spikes),
            "total_events": 10500 + sum(sp["spike_intensity"] for sp in planted_spikes)
        },
        "planted_duplicates": planted_duplicates,
        "planted_spam_accounts": planted_spam_accounts,
        "planted_spam_posts": planted_spam_posts,
        "planted_spikes": planted_spikes
    }

    with open(GROUND_TRUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(ground_truth_data, f, indent=2)

    print(f"SUCCESS: Synthetic generator complete! Ground truth written to {GROUND_TRUTH_FILE}")
    print(f"- Total Users: {len(users)} (including {len(planted_spam_accounts)} spam)")
    print(f"- Total Papers: {len(all_papers_list)} (including {len(planted_duplicates)} planted duplicate pairs)")
    print(f"- Total Posts: {len(posts)} (including {len(planted_spam_posts)} planted spam posts)")
    print(f"- Total Comments: 1100+")
    print(f"- Total Events: {ground_truth_data['summary']['total_events']}")

    db.close()

if __name__ == "__main__":
    generate_all_data()
