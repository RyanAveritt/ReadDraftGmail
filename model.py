from gmail import credentialSetup, readGmail
from transformers import BertTokenizer, BertForMaskedLM, TextDataset, DataCollatorForLanguageModeling, Trainer, TrainingArguments
import pandas as pd

def load_emails():
    #load dataset into dataframe
    return df

def fit(prompt):
    emails = load_emails()
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    tokenized_emails = [tokenizer.encode(email) for email in emails]
    text_dataset = TextDataset(tokenized_emails, tokenizer=tokenizer)
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=True, mlm_probability=0.15)

    model = BertForMaskedLM.from_pretrained('bert-base-uncased')
    training_args = TrainingArguments(
        output_dir='./results',
        overwrite_output_dir=True,
        num_train_epochs=1,
        per_device_train_batch_size=16,
        save_steps=10_000,
        save_total_limit=2,
        prediction_loss_only=True,
        learning_rate=2e-5,
        adam_epsilon=1e-8,
        seed=42,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=text_dataset,
    )
    trainer.train()
    
    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False, return_tensors='pt')
    generated_ids = model.generate(prompt_ids, max_length=50, do_sample=True)
    generated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    return generated_text


